package com.lingua.util;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class SrtUtil {
  public static class Line {
    public int index;
    public double startSeconds;
    public double endSeconds;
    public String text;
  }

  public static List<Line> read(Path path) throws IOException {
    List<Line> out = new ArrayList<>();
    String content = Files.readString(path);
    String[] blocks = content.split("(?m)(?:\\r?\\n){1}\\s*(?:\\r?\\n)+");
    for (String b : blocks) {
      String[] lines = b.split("\r?\n");
      if (lines.length < 2) continue;
      try {
        int idx = Integer.parseInt(lines[0].trim());
        String[] times = lines[1].split("-->");
        double s = parseTime(times[0].trim());
        double e = parseTime(times[1].trim());
        StringBuilder sb = new StringBuilder();
        for (int i=2;i<lines.length;i++) sb.append(lines[i]).append("\n");
        String text = stripHtmlTags(sb.toString().trim());
        Line ln = new Line();
        ln.index = idx;
        ln.startSeconds = s;
        ln.endSeconds = e;
        ln.text = text;
        out.add(ln);
      } catch (Exception ignore) {}
    }
    return out;
  }

  public static Path writeFromJson(Path path, Map<String,Object> json) throws IOException {
    Object raw = json.get("lines");
    if (!(raw instanceof List)) throw new IllegalArgumentException("lines missing");
    @SuppressWarnings("unchecked")
    List<Map<String,Object>> lines = (List<Map<String,Object>>) raw;
    StringBuilder sb = new StringBuilder();
    int counter = 1;
    for (Map<String,Object> l : lines) {
      Object so = l.get("start_time");
      Object eo = l.get("end_time");
      double s = so instanceof Number ? ((Number)so).doubleValue() : Double.parseDouble(String.valueOf(so));
      double e = eo instanceof Number ? ((Number)eo).doubleValue() : Double.parseDouble(String.valueOf(eo));
      String t = (String) l.get("text");
      sb.append(counter).append("\n");
      sb.append(formatTime(s)).append(" --> ").append(formatTime(e)).append("\n");
      sb.append(t == null ? "" : t).append("\n\n");
      counter++;
    }
    Files.createDirectories(path.getParent());
    Files.writeString(path, sb.toString());
    return path;
  }

  private static double parseTime(String srt) {
    String[] hms = srt.replace(',', '.').split(":");
    int h = Integer.parseInt(hms[0]);
    int m = Integer.parseInt(hms[1]);
    double sec = Double.parseDouble(hms[2]);
    return h*3600 + m*60 + sec;
  }

  private static String formatTime(double seconds) {
    int h = (int)(seconds/3600);
    int m = (int)((seconds%3600)/60);
    int s = (int)(seconds%60);
    int ms = (int)((seconds*1000)%1000);
    return String.format("%02d:%02d:%02d,%03d", h, m, s, ms);
  }

  private static String stripHtmlTags(String text) {
    if (text == null || text.isEmpty()) return text;
    // Remove HTML tags and decode common entities
    String cleaned = text
      .replaceAll("<[^>]+>", "") // Remove all HTML tags
      .replace("&nbsp;", " ")
      .replace("&amp;", "&")
      .replace("&lt;", "<")
      .replace("&gt;", ">")
      .replace("&quot;", "\"")
      .replace("&#39;", "'")
      .trim();
    // Remove SSA/ASS positioning tags like {\an8}
    cleaned = cleaned.replaceAll("\\{[^}]+\\}", "");
    return cleaned.trim();
  }
}
