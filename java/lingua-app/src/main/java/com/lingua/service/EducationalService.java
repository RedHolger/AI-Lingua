package com.lingua.service;

import com.lingua.client.AiAgentClient;
import com.lingua.util.SrtUtil;
import java.nio.file.Path;
import java.util.*;

public class EducationalService {
  private final AiAgentClient ai;
  public EducationalService(AiAgentClient ai) { this.ai = ai; }

  public Map<String,Object> analyzeScene(List<SrtUtil.Line> lines) throws Exception {
    List<Map<String,Object>> jsonLines = new ArrayList<>();
    for (SrtUtil.Line l : lines) {
      Map<String,Object> m = new HashMap<>();
      m.put("text", l.text);
      jsonLines.add(m);
    }
    Map<String,Object> payload = new HashMap<>();
    payload.put("lines", jsonLines);
    return ai.analyzeLanguage(payload);
  }

  public Path generatePreviews(Map<String,Object> sceneList, Map<String,Object> elements, Path out) throws Exception {
    Map<String,Object> payload = new HashMap<>();
    payload.put("scenes", sceneList);
    payload.put("elements", elements);
    Map<String,Object> res = ai.generatePreviews(payload);
    return SrtUtil.writeFromJson(out, res);
  }

  public Path generateRecaps(Map<String,Object> elements, Path out) throws Exception {
    Map<String,Object> payload = new HashMap<>();
    payload.put("elements", elements);
    Map<String,Object> res = ai.generateRecaps(payload);
    return SrtUtil.writeFromJson(out, res);
  }

  public Path generateQuizzes(Map<String,Object> aggregated, Path out) throws Exception {
    Map<String,Object> res = ai.generateQuizzes(aggregated);
    java.nio.file.Files.createDirectories(out.getParent());
    String json = new com.fasterxml.jackson.databind.ObjectMapper().writerWithDefaultPrettyPrinter().writeValueAsString(res);
    java.nio.file.Files.writeString(out, json);
    return out;
  }
}
