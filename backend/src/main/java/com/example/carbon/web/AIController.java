package com.example.carbon.web;

import com.example.carbon.service.AIService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/api/ai")
@CrossOrigin(origins = "*")
public class AIController {
    
    @Autowired
    private AIService aiService;
    
    /**
     * 预测碳排放
     */
    @PostMapping("/predict")
    // @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")  // 临时注释掉权限检查
    public CompletableFuture<ResponseEntity<Map<String, Object>>> predictEmissions(
            @RequestParam String industry,
            @RequestParam String resourceType,
            @RequestParam(defaultValue = "12") int timePeriod) {
        
        return aiService.predictEmissions(industry, resourceType, timePeriod)
                .thenApply(result -> ResponseEntity.ok(result))
                .exceptionally(throwable -> {
                    Map<String, Object> error = new HashMap<>();
                    error.put("success", false);
                    error.put("error", "AI服务调用失败: " + throwable.getCause().getMessage());
                    error.put("detail", "请检查Python AI服务是否正在运行 (端口8000)");
                    error.put("timestamp", System.currentTimeMillis());
                    return ResponseEntity.internalServerError().body(error);
                });
    }
    
    /**
     * 检测异常
     */
    @PostMapping("/anomalies")
    // @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")  // 临时注释掉权限检查
    public CompletableFuture<ResponseEntity<Map<String, Object>>> detectAnomalies(
            @RequestParam String industry,
            @RequestParam(defaultValue = "30") int timeRange) {
        
        return aiService.detectAnomalies(industry, timeRange)
                .thenApply(result -> ResponseEntity.ok(result))
                .exceptionally(throwable -> {
                    Map<String, Object> error = new HashMap<>();
                    error.put("success", false);
                    error.put("error", "AI服务调用失败: " + throwable.getCause().getMessage());
                    error.put("detail", "请检查Python AI服务是否正在运行 (端口8000)");
                    error.put("timestamp", System.currentTimeMillis());
                    return ResponseEntity.internalServerError().body(error);
                });
    }
    
    /**
     * 分析碳循环
     */
    @PostMapping("/carbon-cycle")
    // @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")  // 临时注释掉权限检查
    public CompletableFuture<ResponseEntity<Map<String, Object>>> analyzeCarbonCycle(
            @RequestParam String region,
            @RequestParam(defaultValue = "3") int timePeriod) {
        
        return aiService.analyzeCarbonCycle(region, timePeriod)
                .thenApply(result -> ResponseEntity.ok(result))
                .exceptionally(throwable -> {
                    Map<String, Object> error = new HashMap<>();
                    error.put("success", false);
                    error.put("error", throwable.getCause().getMessage());
                    return ResponseEntity.internalServerError().body(error);
                });
    }
    
    /**
     * 启动数据采集
     */
    @PostMapping("/collect")
    @PreAuthorize("hasRole('ADMIN')")
    public CompletableFuture<ResponseEntity<Map<String, Object>>> startDataCollection(
            @RequestParam String sourceType,
            @RequestParam(required = false) String industry,
            @RequestParam(required = false) String region) {
        
        return aiService.startDataCollection(sourceType, industry, region)
                .thenApply(result -> ResponseEntity.ok(result))
                .exceptionally(throwable -> {
                    Map<String, Object> error = new HashMap<>();
                    error.put("success", false);
                    error.put("error", throwable.getCause().getMessage());
                    return ResponseEntity.internalServerError().body(error);
                });
    }
    
    /**
     * 获取任务状态
     */
    @GetMapping("/tasks/status")
    @PreAuthorize("hasRole('ADMIN') or hasRole('USER')")
    public ResponseEntity<Map<String, Object>> getTaskStatus() {
        try {
            Map<String, Object> status = aiService.getTaskStatus();
            return ResponseEntity.ok(status);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("error", e.getMessage());
            return ResponseEntity.internalServerError().body(error);
        }
    }
    
    /**
     * 检查AI服务健康状态
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> checkHealth() {
        try {
            boolean isHealthy = aiService.isHealthy();
            Map<String, Object> response = new HashMap<>();
            response.put("service", "AI服务");
            response.put("status", isHealthy ? "healthy" : "unhealthy");
            response.put("timestamp", System.currentTimeMillis());
            response.put("message", "后端AI服务运行正常");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("service", "AI服务");
            response.put("status", "error");
            response.put("error", e.getMessage());
            response.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.status(503).body(response);
        }
    }
    
    /**
     * 获取支持的行业类型
     */
    @GetMapping("/industries")
    public ResponseEntity<Map<String, Object>> getSupportedIndustries() {
        Map<String, Object> industries = new HashMap<>();
        
        String[] industryArray = {
            "manufacturing", "energy", "transportation", "agriculture",
            "construction", "services", "mining", "chemical"
        };
        industries.put("industries", industryArray);
        
        Map<String, String> descriptions = new HashMap<>();
        descriptions.put("manufacturing", "制造业");
        descriptions.put("energy", "能源");
        descriptions.put("transportation", "交通");
        descriptions.put("agriculture", "农业");
        descriptions.put("construction", "建筑");
        descriptions.put("services", "服务业");
        descriptions.put("mining", "采矿业");
        descriptions.put("chemical", "化工业");
        industries.put("descriptions", descriptions);
        
        return ResponseEntity.ok(industries);
    }
    
    /**
     * 获取支持的资源类型
     */
    @GetMapping("/resources")
    public ResponseEntity<Map<String, Object>> getSupportedResources() {
        Map<String, Object> resources = new HashMap<>();
        
        String[] resourceArray = {
            "coal", "oil", "gas", "electricity", "renewable", "nuclear"
        };
        resources.put("resources", resourceArray);
        
        Map<String, String> descriptions = new HashMap<>();
        descriptions.put("coal", "煤炭");
        descriptions.put("oil", "石油");
        descriptions.put("gas", "天然气");
        descriptions.put("electricity", "电力");
        descriptions.put("renewable", "可再生能源");
        descriptions.put("nuclear", "核能");
        resources.put("descriptions", descriptions);
        
        return ResponseEntity.ok(resources);
    }
    
    /**
     * 获取支持的数据源类型
     */
    @GetMapping("/data-sources")
    public ResponseEntity<Map<String, Object>> getSupportedDataSources() {
        Map<String, Object> sources = new HashMap<>();
        
        String[] sourceArray = {
            "web_scraping", "energy_logs", "remote_sensing", "public_data", "modis"
        };
        sources.put("sources", sourceArray);
        
        Map<String, String> descriptions = new HashMap<>();
        descriptions.put("web_scraping", "网络爬虫");
        descriptions.put("energy_logs", "能源日志");
        descriptions.put("remote_sensing", "遥感数据");
        descriptions.put("public_data", "公开数据");
        descriptions.put("modis", "MODIS卫星数据");
        sources.put("descriptions", descriptions);
        
        return ResponseEntity.ok(sources);
    }
} 