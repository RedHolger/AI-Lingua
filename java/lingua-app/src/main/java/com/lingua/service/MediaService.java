package com.lingua.service;

import org.springframework.stereotype.Service;
import java.nio.file.*;
import java.io.*;
import java.util.*;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class MediaService {
  public Path extractEmbeddedSubtitles(Path mediaPath) throws Exception {
    Path mediaPathAbs = mediaPath.toAbsolutePath();
    // Output to data/output relative to project root (media is under data/input)
    Path mediaParent = mediaPathAbs.getParent(); // .../data/input
    Path projectRoot = mediaParent.getParent() != null && mediaParent.getParent().getParent() != null
      ? mediaParent.getParent().getParent() // go up two levels from data/input to project root
      : mediaPathAbs.getParent();
    Path out = projectRoot.resolve("data/output").resolve(mediaPathAbs.getFileName().toString() + ".embedded.srt");
    
    // Check if already extracted
    if (Files.exists(out)) {
      return out;
    }
    
    Files.createDirectories(out.getParent());
    ProcessBuilder pb = new ProcessBuilder(
      "ffprobe","-v","error","-select_streams","s","-show_entries","stream=index:stream_tags=language,title","-of","json", mediaPathAbs.toString()
    );
    Process p = pb.start();
    String json = new String(p.getInputStream().readAllBytes());
    String errorOutput = new String(p.getErrorStream().readAllBytes());
    int code = p.waitFor();
    if (code != 0 || json.isEmpty()) {
      System.err.println("FFprobe failed with code " + code + ": " + errorOutput);
      return null;
    }
    Integer idx = null;
    try {
      Map<?,?> root = new ObjectMapper().readValue(json, Map.class);
      Object streamsObj = root.get("streams");
      if (streamsObj instanceof List<?>) {
        List<?> streams = (List<?>) streamsObj;
        if (!streams.isEmpty()) {
          // Prefer first subtitle stream; if language preference needed, enhance here
          Object first = streams.get(0);
          if (first instanceof Map<?,?>) {
            Map<?,?> m = (Map<?,?>) first;
            Object indexVal = m.get("index");
            if (indexVal instanceof Number) {
              idx = ((Number) indexVal).intValue();
            } else if (indexVal != null) {
              try { idx = Integer.parseInt(indexVal.toString()); } catch (NumberFormatException ignored) {}
            }
          }
        }
      }
    } catch (Exception e) {
      System.err.println("Failed to parse ffprobe JSON: " + e.getMessage());
    }
    if (idx == null) {
      System.err.println("No subtitle stream index could be determined from ffprobe output.");
      return null;
    }
    String index = Integer.toString(idx);
    ProcessBuilder ff = new ProcessBuilder(
      "ffmpeg","-y","-i", mediaPathAbs.toString(),"-map","0:"+index,"-c:s","srt", out.toString()
    );
    Process pf = ff.start();
    String ffmpegOutput = new String(pf.getInputStream().readAllBytes());
    String ffmpegError = new String(pf.getErrorStream().readAllBytes());
    int ec = pf.waitFor();
    if (ec != 0) {
      System.err.println("FFmpeg failed with code " + ec + ": " + ffmpegError);
      return null;
    }
    return Files.exists(out) ? out : null;
  }
}
