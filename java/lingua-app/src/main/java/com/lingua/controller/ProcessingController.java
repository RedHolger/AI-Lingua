package com.lingua.controller;

import org.springframework.web.bind.annotation.*;
import com.lingua.service.MediaService;
import com.lingua.client.AiAgentClient;
import com.lingua.util.SrtUtil;
import com.lingua.service.SceneService;
import com.lingua.service.EducationalService;
import com.lingua.service.PlaybackService;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

@RestController
@RequestMapping("/api")
public class ProcessingController {
  private final MediaService mediaService;
  private final AiAgentClient aiAgentClient;
  private final PlaybackService playbackService = new PlaybackService();

  public ProcessingController(MediaService mediaService) {
    this.mediaService = mediaService;
    this.aiAgentClient = new AiAgentClient(System.getProperty("ai.service.url","http://localhost:8001"));
  }

  private Path resolveProjectPath(String relativePath) {
    // Spring Boot runs from java/lingua-app, so go up two levels to project root
    Path projectRoot = Paths.get(System.getProperty("user.dir")).getParent().getParent();
    return projectRoot.resolve(relativePath).toAbsolutePath().normalize();
  }

  @PostMapping("/process")
  public Map<String,Object> process(@RequestBody Map<String,Object> req) throws Exception {
    String mediaPath = (String)req.get("mediaPath");
    Boolean useEmbedded = Boolean.TRUE.equals(req.get("useEmbedded"));
    String officialSrt = (String)req.getOrDefault("officialSrt", null);
    Boolean generatePreviews = Boolean.TRUE.equals(req.get("generatePreviews"));
    Boolean generateRecaps = Boolean.TRUE.equals(req.get("generateRecaps"));
    Boolean generateQuizzes = Boolean.TRUE.equals(req.get("generateQuizzes"));
    double gap = req.get("gapThreshold") instanceof Number ? ((Number)req.get("gapThreshold")).doubleValue() : 3.0;
    String learnerLevel = (String)req.getOrDefault("learnerLevel","A1");
    Path originalSrt;
    if (officialSrt != null && !officialSrt.isEmpty()) {
      originalSrt = resolveProjectPath(officialSrt);
    } else if (useEmbedded) {
      Path mediaPathAbs = resolveProjectPath(mediaPath);
      originalSrt = mediaService.extractEmbeddedSubtitles(mediaPathAbs);
    } else {
      originalSrt = null;
    }
    if (originalSrt == null) {
      throw new IllegalStateException("No official subtitles available");
    }
    List<SrtUtil.Line> lines = SrtUtil.read(originalSrt);
    List<Map<String,Object>> jsonLines = new ArrayList<>();
    for (SrtUtil.Line l : lines) {
      Map<String,Object> m = new HashMap<>();
      m.put("start_time", l.startSeconds);
      m.put("end_time", l.endSeconds);
      m.put("text", l.text);
      jsonLines.add(m);
    }
    
    // Batch process simplification to handle large files
    List<Map<String,Object>> allSimplifiedLines = new ArrayList<>();
    int batchSize = 100; // Process 100 lines at a time
    for (int i = 0; i < jsonLines.size(); i += batchSize) {
      int end = Math.min(i + batchSize, jsonLines.size());
      List<Map<String,Object>> batch = jsonLines.subList(i, end);
      Map<String,Object> payload = new HashMap<>();
      payload.put("lines", batch);
      payload.put("learnerLevel", learnerLevel);
      try {
        Map<String,Object> batchResult = aiAgentClient.simplify(payload);
        @SuppressWarnings("unchecked")
        List<Map<String,Object>> batchLines = (List<Map<String,Object>>) batchResult.get("lines");
        if (batchLines != null) {
          allSimplifiedLines.addAll(batchLines);
        }
        // Small delay between batches to avoid rate limiting
        Thread.sleep(500);
      } catch (Exception e) {
        System.err.println("Error processing batch " + (i/batchSize + 1) + ": " + e.getMessage());
        // Fallback: use original lines if simplification fails
        allSimplifiedLines.addAll(batch);
      }
    }
    Map<String,Object> simplified = new HashMap<>();
    simplified.put("lines", allSimplifiedLines);
    Path outDir = resolveProjectPath("data/output");
    Files.createDirectories(outDir);
    Path simplifiedSrt = SrtUtil.writeFromJson(outDir.resolve("simplified.srt"), simplified);
    Map<String,Object> out = new HashMap<>();
    out.put("originalSrt", originalSrt.toString());
    out.put("simplifiedSrt", simplifiedSrt.toString());

    SceneService sceneService = new SceneService();
    List<SceneService.Scene> scenes = sceneService.segment(lines, gap);
    Map<String,Object> sceneListJson = new HashMap<>();
    List<Map<String,Object>> sceneBlocks = new ArrayList<>();
    for (SceneService.Scene sc : scenes) {
      Map<String,Object> block = new HashMap<>();
      block.put("start", sc.start);
      block.put("end", sc.end);
      List<Map<String,Object>> lns = new ArrayList<>();
      for (SrtUtil.Line l : sc.lines) {
        Map<String,Object> m = new HashMap<>();
        m.put("text", l.text);
        lns.add(m);
      }
      block.put("lines", lns);
      sceneBlocks.add(block);
    }
    sceneListJson.put("scenes", sceneBlocks);

    EducationalService edu = new EducationalService(aiAgentClient);
    Map<String,Object> aggregatedElements = new HashMap<>();
    List<Map<String,Object>> allElements = new ArrayList<>();
    for (SceneService.Scene sc : scenes) {
      try {
        Map<String,Object> el = edu.analyzeScene(sc.lines);
        allElements.add(el);
      } catch (Exception e) {
        System.err.println("Error analyzing scene: " + e.getMessage());
        // Continue with other scenes
      }
    }
    aggregatedElements.put("elements", allElements);
    if (generatePreviews) {
      try {
        Path previewsSrt = edu.generatePreviews(sceneListJson, aggregatedElements, outDir.resolve("previews.srt"));
        out.put("previewsSrt", previewsSrt.toString());
      } catch (Exception e) {
        System.err.println("Error generating previews: " + e.getMessage());
        // Continue without previews
      }
    }
    if (generateRecaps) {
      try {
        Path recapsSrt = edu.generateRecaps(aggregatedElements, outDir.resolve("recaps.srt"));
        out.put("recapsSrt", recapsSrt.toString());
      } catch (Exception e) {
        System.err.println("Error generating recaps: " + e.getMessage());
        // Continue without recaps
      }
    }
    if (generateQuizzes) {
      try {
        Path quizzesJson = edu.generateQuizzes(aggregatedElements, outDir.resolve("quizzes.json"));
        out.put("quizzesJson", quizzesJson.toString());
      } catch (Exception e) {
        System.err.println("Error generating quizzes: " + e.getMessage());
        // Continue without quizzes
      }
    }

    Map<String,String> mpvOpts = new HashMap<>();
    mpvOpts.put("sub-font-size","24");
    mpvOpts.put("secondary-sub-font-size","20");
    mpvOpts.put("secondary-sub-color","#FFFF00");
    Path mpvConf = playbackService.generateMpvConfig(outDir.resolve("playback.mpv.conf"), mpvOpts);
    out.put("mpvConf", mpvConf.toString());
    return out;
  }

  
}
