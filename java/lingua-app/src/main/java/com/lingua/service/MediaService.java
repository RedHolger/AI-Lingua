package com.lingua.service;

import org.springframework.stereotype.Service;
import java.nio.file.*;
import java.io.*;

@Service
public class MediaService {
  public Path extractEmbeddedSubtitles(Path mediaPath) throws Exception {
    Path mediaPathAbs = mediaPath.toAbsolutePath();
    // Output to data/output relative to mediaPath (go up from data/input to project root, then to data/output)
    Path mediaParent = mediaPathAbs.getParent(); // data/input
    Path projectRoot = mediaParent.getParent(); // project root
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
    int idxPos = json.indexOf("\"index\":");
    if (idxPos < 0) {
      System.err.println("No subtitle stream index found in: " + json);
      return null;
    }
    String rest = json.substring(idxPos + 8);
    String num = rest.replaceAll("[^0-9]", "");
    if (num.isEmpty()) {
      System.err.println("Could not extract subtitle index from: " + rest);
      return null;
    }
    String index = num;
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
