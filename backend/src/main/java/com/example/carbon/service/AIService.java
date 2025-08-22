package com.example.carbon.service;

import com.example.carbon.model.EmissionRecord;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import org.springframework.core.ParameterizedTypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;

import java.util.*;
import java.util.concurrent.CompletableFuture;

@Service
public class AIService {
    
    @Value("${python.service.url:http://localhost:8000}")
    private String pythonServiceUrl;
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    public AIService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * 预测碳排放
     */
    public CompletableFuture<Map<String, Object>> predictEmissions(String industry, String resourceType, int timePeriod) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String url = pythonServiceUrl + "/api/predict/emissions";
                
                Map<String, Object> request = new HashMap<>();
                request.put("industry", industry);
                request.put("resource_type", resourceType);
                request.put("time_period", timePeriod);
                
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                
                HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
                
                ResponseEntity<String> response = restTemplate.exchange(
                    url, 
                    HttpMethod.POST, 
                    entity, 
                    String.class
                );
                
                if (response.getStatusCode() == HttpStatus.OK) {
                    return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
                } else {
                    throw new RuntimeException("AI预测服务调用失败: " + response.getStatusCode());
                }
                
            } catch (Exception e) {
                throw new RuntimeException("AI预测服务调用异常: " + e.getMessage(), e);
            }
        });
    }
    
    /**
     * 检测异常
     */
    public CompletableFuture<Map<String, Object>> detectAnomalies(String industry, int timeRange) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String url = pythonServiceUrl + "/api/detect/anomalies";
                
                Map<String, Object> request = new HashMap<>();
                request.put("industry", industry);
                request.put("time_range", timeRange);
                request.put("threshold", 0.95);
                
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                
                HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
                
                ResponseEntity<String> response = restTemplate.exchange(
                    url, 
                    HttpMethod.POST, 
                    entity, 
                    String.class
                );
                
                if (response.getStatusCode() == HttpStatus.OK) {
                    return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
                } else {
                    throw new RuntimeException("异常检测服务调用失败: " + response.getStatusCode());
                }
                
            } catch (Exception e) {
                throw new RuntimeException("异常检测服务调用异常: " + e.getMessage(), e);
            }
        });
    }
    
    /**
     * 分析碳循环
     */
    public CompletableFuture<Map<String, Object>> analyzeCarbonCycle(String region, int timePeriod) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String url = pythonServiceUrl + "/api/analyze/carbon-cycle";
                
                Map<String, Object> request = new HashMap<>();
                request.put("region", region);
                request.put("time_period", timePeriod);
                request.put("include_remote_sensing", true);
                
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                
                HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
                
                ResponseEntity<String> response = restTemplate.exchange(
                    url, 
                    HttpMethod.POST, 
                    entity, 
                    String.class
                );
                
                if (response.getStatusCode() == HttpStatus.OK) {
                    return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
                } else {
                    throw new RuntimeException("碳循环分析服务调用失败: " + response.getStatusCode());
                }
                
            } catch (Exception e) {
                throw new RuntimeException("碳循环分析服务调用异常: " + e.getMessage(), e);
            }
        });
    }
    
    /**
     * 启动数据采集
     */
    public CompletableFuture<Map<String, Object>> startDataCollection(String sourceType, String industry, String region) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String url = pythonServiceUrl + "/api/collect/data";
                
                Map<String, Object> request = new HashMap<>();
                request.put("source_type", sourceType);
                request.put("industry", industry);
                request.put("region", region);
                
                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                
                HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
                
                ResponseEntity<String> response = restTemplate.exchange(
                    url, 
                    HttpMethod.POST, 
                    entity, 
                    String.class
                );
                
                if (response.getStatusCode() == HttpStatus.OK) {
                    return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
                } else {
                    throw new RuntimeException("数据采集服务调用失败: " + response.getStatusCode());
                }
                
            } catch (Exception e) {
                throw new RuntimeException("数据采集服务调用异常: " + e.getMessage(), e);
            }
        });
    }
    
    /**
     * 获取任务状态
     */
    public Map<String, Object> getTaskStatus() {
        try {
            String url = pythonServiceUrl + "/api/status/tasks";
            
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                return objectMapper.readValue(response.getBody(), new TypeReference<Map<String, Object>>() {});
            } else {
                throw new RuntimeException("获取任务状态失败: " + response.getStatusCode());
            }
            
        } catch (Exception e) {
            throw new RuntimeException("获取任务状态异常: " + e.getMessage(), e);
        }
    }
    
    /**
     * 检查AI服务健康状态
     */
    public boolean isHealthy() {
        try {
            String url = pythonServiceUrl + "/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            return false;
        }
    }
} 