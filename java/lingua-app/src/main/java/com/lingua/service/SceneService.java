package com.lingua.service;

import com.lingua.util.SrtUtil;
import java.util.*;

public class SceneService {
  public static class Scene {
    public double start;
    public double end;
    public List<SrtUtil.Line> lines;
  }

  public List<Scene> segment(List<SrtUtil.Line> lines, double gapThreshold) {
    List<Scene> scenes = new ArrayList<>();
    List<SrtUtil.Line> current = new ArrayList<>();
    Double lastEnd = null;
    for (SrtUtil.Line ln : lines) {
      if (lastEnd != null && ln.startSeconds - lastEnd >= gapThreshold) {
        if (!current.isEmpty()) {
          Scene sc = new Scene();
          sc.start = current.get(0).startSeconds;
          sc.end = current.get(current.size() - 1).endSeconds;
          sc.lines = new ArrayList<>(current);
          scenes.add(sc);
          current.clear();
        }
      }
      current.add(ln);
      lastEnd = ln.endSeconds;
    }
    if (!current.isEmpty()) {
      Scene sc = new Scene();
      sc.start = current.get(0).startSeconds;
      sc.end = current.get(current.size() - 1).endSeconds;
      sc.lines = new ArrayList<>(current);
      scenes.add(sc);
    }
    return scenes;
  }

  public Map<String,Object> generatePreviews(List<Scene> scenes, double leadSeconds, int wordsK, int phrasesK) {
    List<Map<String,Object>> out = new ArrayList<>();
    for (Scene sc : scenes) {
      List<String> texts = new ArrayList<>();
      for (SrtUtil.Line l : sc.lines) texts.add(l.text);
      List<String> topw = topWords(texts, wordsK);
      List<String> phrases = shortPhrases(texts, phrasesK);
      double start = Math.max(0.0, sc.start - leadSeconds);
      double t = start;
      List<String> items = new ArrayList<>();
      if (!topw.isEmpty()) items.add("Words: " + String.join(", ", topw));
      for (String p : phrases) items.add("Phrase: " + p);
      for (String item : items) {
        double end = t + 3.0;
        Map<String,Object> m = new HashMap<>();
        m.put("start_time", t);
        m.put("end_time", end);
        m.put("text", item);
        out.add(m);
        t = end;
      }
    }
    Map<String,Object> res = new HashMap<>();
    res.put("lines", out);
    return res;
  }

  public Map<String,Object> generateRecaps(List<Scene> scenes) {
    List<Map<String,Object>> out = new ArrayList<>();
    for (Scene sc : scenes) {
      List<String> texts = new ArrayList<>();
      for (SrtUtil.Line l : sc.lines) texts.add(l.text);
      List<String> vocab = topVocab(texts, 8);
      List<String> phrases = phrases(texts, 3);
      List<String> grammar = grammarNotes(texts);
      double t = sc.end;
      List<String> items = new ArrayList<>();
      if (!vocab.isEmpty()) items.add("Vocab: " + String.join(", ", vocab));
      for (String p : phrases) items.add("Phrase: " + p);
      if (!grammar.isEmpty()) items.add("Grammar: " + String.join(", ", grammar));
      for (String item : items) {
        double end = t + 4.0;
        Map<String,Object> m = new HashMap<>();
        m.put("start_time", t);
        m.put("end_time", end);
        m.put("text", item);
        out.add(m);
        t = end;
      }
    }
    Map<String,Object> res = new HashMap<>();
    res.put("lines", out);
    return res;
  }

  private static final Set<String> STOP = new HashSet<>(Arrays.asList(
    "the","a","an","and","or","but","to","of","in","on","for","with","at","by","from","as","is","are","was","were","be","been","am","i","you","he","she","it","we","they","me","him","her","them","my","your","his","her","its","our","their","this","that","these","those"
  ));

  private List<String> words(String s) {
    List<String> out = new ArrayList<>();
    String[] parts = s.split("[^A-Za-z']+");
    for (String p : parts) if (!p.isEmpty()) out.add(p.toLowerCase());
    return out;
  }

  private List<String> topWords(List<String> lines, int k) {
    Map<String,Integer> freq = new HashMap<>();
    for (String ln : lines) for (String w : words(ln)) {
      if (STOP.contains(w)) continue;
      freq.put(w, freq.getOrDefault(w, 0) + 1);
    }
    List<Map.Entry<String,Integer>> list = new ArrayList<>(freq.entrySet());
    list.sort((a,b) -> {
      int c = Integer.compare(b.getValue(), a.getValue());
      return c != 0 ? c : a.getKey().compareTo(b.getKey());
    });
    List<String> res = new ArrayList<>();
    for (int i=0; i<Math.min(k, list.size()); i++) res.add(list.get(i).getKey());
    return res;
  }

  private List<String> shortPhrases(List<String> lines, int k) {
    List<String> ph = new ArrayList<>();
    for (String ln : lines) {
      String t = ln.trim();
      if (!t.isEmpty() && t.length() <= 60) ph.add(t);
    }
    return ph.size() > k ? ph.subList(0,k) : ph;
  }

  private List<String> topVocab(List<String> lines, int k) {
    Map<String,Integer> freq = new HashMap<>();
    for (String ln : lines) for (String w : words(ln)) {
      if (w.length() <= 2) continue;
      freq.put(w, freq.getOrDefault(w, 0) + 1);
    }
    List<Map.Entry<String,Integer>> list = new ArrayList<>(freq.entrySet());
    list.sort((a,b) -> {
      int c = Integer.compare(b.getValue(), a.getValue());
      return c != 0 ? c : a.getKey().compareTo(b.getKey());
    });
    List<String> res = new ArrayList<>();
    for (int i=0; i<Math.min(k, list.size()); i++) res.add(list.get(i).getKey());
    return res;
  }

  private List<String> phrases(List<String> lines, int k) {
    List<String> ph = new ArrayList<>();
    for (String ln : lines) {
      String t = ln.trim();
      if (t.length() >= 20 && t.length() <= 80) ph.add(t);
    }
    return ph.size() > k ? ph.subList(0,k) : ph;
  }

  private List<String> grammarNotes(List<String> lines) {
    List<String> notes = new ArrayList<>();
    boolean q = false, neg = false, fut = false, past = false;
    for (String ln : lines) {
      if (ln.contains("?")) q = true;
      String low = ln.toLowerCase();
      if (low.contains("n't") || low.contains(" not ")) neg = true;
      if (low.contains(" will ") || low.contains("going to")) fut = true;
      if (low.contains(" was ") || low.contains(" were ") || low.contains(" had ")) past = true;
    }
    if (q) notes.add("Questions used");
    if (neg) notes.add("Negation patterns");
    if (fut) notes.add("Future constructions");
    if (past) notes.add("Past forms");
    if (notes.isEmpty()) notes.add("Core sentence patterns");
    return notes;
  }
}
