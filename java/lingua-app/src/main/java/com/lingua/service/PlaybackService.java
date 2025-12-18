package com.lingua.service;

import java.nio.file.*;
import java.util.*;

public class PlaybackService {
  public Path generateMpvConfig(Path out, Map<String,String> opts) throws Exception {
    StringBuilder sb = new StringBuilder();
    for (Map.Entry<String,String> e : opts.entrySet()) {
      sb.append(e.getKey()).append("=").append(e.getValue()).append("\n");
    }
    Files.createDirectories(out.getParent());
    Files.writeString(out, sb.toString());
    return out;
  }
}
