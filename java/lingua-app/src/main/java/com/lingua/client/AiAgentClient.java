package com.lingua.client;

import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.CloseableHttpResponse;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.client5.http.config.RequestConfig;
import org.apache.hc.core5.http.ContentType;
import org.apache.hc.core5.http.HttpEntity;
import org.apache.hc.core5.http.io.entity.StringEntity;
import com.fasterxml.jackson.databind.ObjectMapper;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.TimeUnit;

public class AiAgentClient {
  private final String baseUrl;
  private final ObjectMapper mapper = new ObjectMapper();
  private final String hmacSecret;

  public AiAgentClient(String baseUrl) {
    this.baseUrl = baseUrl;
    this.hmacSecret = System.getProperty("ai.hmac.secret", System.getenv("AI_HMAC_SECRET"));
  }

  private String sign(String payload) throws Exception {
    if (hmacSecret == null || hmacSecret.isEmpty()) return null;
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(hmacSecret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
    byte[] sig = mac.doFinal(payload.getBytes(StandardCharsets.UTF_8));
    StringBuilder sb = new StringBuilder();
    for (byte b : sig) sb.append(String.format("%02x", b));
    return sb.toString();
  }

  private Map<String,Object> postJson(String path, Map<String,Object> payload) throws Exception {
    RequestConfig config = RequestConfig.custom()
      .setConnectTimeout(30, TimeUnit.SECONDS)
      .setResponseTimeout(300, TimeUnit.SECONDS) // 5 minutes for AI processing
      .build();
    try (CloseableHttpClient client = HttpClients.custom()
      .setDefaultRequestConfig(config)
      .build()) {
      HttpPost post = new HttpPost(baseUrl + path);
      String json = mapper.writeValueAsString(payload);
      post.setEntity(new StringEntity(json, ContentType.APPLICATION_JSON));
      post.setHeader("Accept","application/json");
      String signature = sign(json);
      if (signature != null) post.setHeader("X-Signature", signature);
      try (CloseableHttpResponse resp = client.execute(post)) {
        int code = resp.getCode();
        if (code < 200 || code >= 300) throw new IllegalStateException("AI service HTTP " + code);
        HttpEntity entity = resp.getEntity();
        byte[] body = entity != null ? entity.getContent().readAllBytes() : new byte[0];
        if (body.length == 0) throw new IllegalStateException("Empty AI response");
        return mapper.readValue(body, Map.class);
      }
    }
  }

  public Map<String,Object> simplify(Map<String,Object> payload) throws Exception {
    return postJson("/simplify", payload);
  }

  public Map<String,Object> analyzeLanguage(Map<String,Object> payload) throws Exception {
    return postJson("/analyze_language", payload);
  }

  public Map<String,Object> generatePreviews(Map<String,Object> payload) throws Exception {
    return postJson("/generate_previews", payload);
  }

  public Map<String,Object> generateRecaps(Map<String,Object> payload) throws Exception {
    return postJson("/generate_recaps", payload);
  }

  public Map<String,Object> generateQuizzes(Map<String,Object> payload) throws Exception {
    return postJson("/generate_quizzes", payload);
  }
}
