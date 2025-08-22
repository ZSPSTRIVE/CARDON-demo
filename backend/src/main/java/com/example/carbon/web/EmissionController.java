package com.example.carbon.web;

import com.example.carbon.model.EmissionRecord;
import com.example.carbon.service.EmissionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/emissions")
@CrossOrigin(origins = "*")
public class EmissionController {

    @Autowired
    private EmissionService emissionService;

    @GetMapping("/line")
    public ResponseEntity<Map<String, Object>> getLineData(
            @RequestParam(defaultValue = "2022-01-01") String start,
            @RequestParam(defaultValue = "2022-12-31") String end) {
        
        try {
            // 生成模拟数据
            Map<String, Object> data = generateLineData(start, end);
            return ResponseEntity.ok(data);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/heatmap")
    public ResponseEntity<List<Map<String, Object>>> getHeatmapData(
            @RequestParam(defaultValue = "2022-01-01") String start,
            @RequestParam(defaultValue = "2022-12-31") String end) {
        
        try {
            List<Map<String, Object>> data = generateHeatmapData(start, end);
            return ResponseEntity.ok(data);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(Arrays.asList(error));
        }
    }

    @GetMapping("/bar")
    public ResponseEntity<List<Map<String, Object>>> getBarData(
            @RequestParam(defaultValue = "2022-01-01") String start,
            @RequestParam(defaultValue = "2022-12-31") String end,
            @RequestParam(defaultValue = "industry") String groupBy) {
        
        try {
            List<Map<String, Object>> data = generateBarData(start, end, groupBy);
            return ResponseEntity.ok(data);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(Arrays.asList(error));
        }
    }

    @GetMapping("/dashboard-summary")
    public ResponseEntity<Map<String, Object>> getDashboardSummary() {
        try {
            Map<String, Object> summary = generateDashboardSummary();
            return ResponseEntity.ok(summary);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/industry-distribution")
    public ResponseEntity<Map<String, Object>> getIndustryDistribution() {
        try {
            Map<String, Object> data = generateIndustryDistribution();
            return ResponseEntity.ok(data);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/resource-analysis")
    public ResponseEntity<Map<String, Object>> getResourceAnalysis() {
        try {
            Map<String, Object> data = generateResourceAnalysis();
            return ResponseEntity.ok(data);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    @GetMapping("/data-details")
    public ResponseEntity<Map<String, Object>> getDataDetails(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        try {
            Map<String, Object> data = generateDataDetails(page, size);
            return ResponseEntity.ok(data);
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error", "数据获取失败: " + e.getMessage());
            return ResponseEntity.badRequest().body(error);
        }
    }

    // 生成模拟数据的方法
    private Map<String, Object> generateLineData(String start, String end) {
        Map<String, Object> data = new HashMap<>();
        
        // 生成时间序列
        List<Map<String, Object>> totalData = new ArrayList<>();
        Map<String, List<Map<String, Object>>> byIndustry = new HashMap<>();
        Map<String, List<Map<String, Object>>> byResource = new HashMap<>();
        
        LocalDate startDate = LocalDate.parse(start);
        LocalDate endDate = LocalDate.parse(end);
        
        String[] industries = {"manufacturing", "energy", "transportation", "agriculture", "construction", "services", "mining", "chemical"};
        String[] resources = {"coal", "oil", "gas", "electricity", "renewable", "nuclear"};
        
        // 初始化行业和资源数据
        for (String industry : industries) {
            byIndustry.put(industry, new ArrayList<>());
        }
        for (String resource : resources) {
            byResource.put(resource, new ArrayList<>());
        }
        
        LocalDate currentDate = startDate;
        int dayCount = 0;
        
        while (!currentDate.isAfter(endDate)) {
            String dateStr = currentDate.format(DateTimeFormatter.ISO_LOCAL_DATE);
            
            // 基础排放量
            double baseEmission = 1000 + Math.sin(dayCount * 0.1) * 200 + Math.random() * 100;
            
            // 总量数据
            Map<String, Object> totalItem = new HashMap<>();
            totalItem.put("date", dateStr);
            totalItem.put("value", Math.round(baseEmission));
            totalData.add(totalItem);
            
            // 行业数据
            for (String industry : industries) {
                double industryFactor = getIndustryFactor(industry);
                double seasonalFactor = 1 + 0.3 * Math.sin(2 * Math.PI * dayCount / 365);
                double emission = baseEmission * industryFactor * seasonalFactor * (0.8 + Math.random() * 0.4);
                
                Map<String, Object> industryItem = new HashMap<>();
                industryItem.put("date", dateStr);
                industryItem.put("value", Math.round(emission));
                byIndustry.get(industry).add(industryItem);
            }
            
            // 资源数据
            for (String resource : resources) {
                double resourceFactor = getResourceFactor(resource);
                double seasonalFactor = 1 + 0.2 * Math.cos(2 * Math.PI * dayCount / 365);
                double emission = baseEmission * resourceFactor * seasonalFactor * (0.7 + Math.random() * 0.6);
                
                Map<String, Object> resourceItem = new HashMap<>();
                resourceItem.put("date", dateStr);
                resourceItem.put("value", Math.round(emission));
                byResource.get(resource).add(resourceItem);
            }
            
            currentDate = currentDate.plusDays(1);
            dayCount++;
        }
        
        data.put("total", totalData);
        data.put("byIndustry", byIndustry);
        data.put("byResource", byResource);
        
        return data;
    }

    private List<Map<String, Object>> generateHeatmapData(String start, String end) {
        List<Map<String, Object>> data = new ArrayList<>();
        
        String[] industries = {"manufacturing", "energy", "transportation", "agriculture", "construction", "services", "mining", "chemical"};
        String[] resources = {"coal", "oil", "gas", "electricity", "renewable", "nuclear"};
        
        for (String industry : industries) {
            for (String resource : resources) {
                Map<String, Object> item = new HashMap<>();
                item.put("industry", industry);
                item.put("resource", resource);
                
                // 生成基于行业和资源类型的排放量
                double industryFactor = getIndustryFactor(industry);
                double resourceFactor = getResourceFactor(resource);
                double baseValue = 500 + Math.random() * 1000;
                double value = baseValue * industryFactor * resourceFactor * (0.5 + Math.random());
                
                item.put("value", Math.round(value));
                data.add(item);
            }
        }
        
        return data;
    }

    private List<Map<String, Object>> generateBarData(String start, String end, String groupBy) {
        List<Map<String, Object>> data = new ArrayList<>();
        
        if ("industry".equals(groupBy)) {
            String[] industries = {"manufacturing", "energy", "transportation", "agriculture", "construction", "services", "mining", "chemical"};
            for (String industry : industries) {
                Map<String, Object> item = new HashMap<>();
                item.put("name", industry);
                double value = 1000 + Math.random() * 2000;
                item.put("value", Math.round(value));
                data.add(item);
            }
        } else if ("resource".equals(groupBy)) {
            String[] resources = {"coal", "oil", "gas", "electricity", "renewable", "nuclear"};
            for (String resource : resources) {
                Map<String, Object> item = new HashMap<>();
                item.put("name", resource);
                double value = 800 + Math.random() * 1500;
                item.put("value", Math.round(value));
                data.add(item);
            }
        }
        
        return data;
    }

    private Map<String, Object> generateDashboardSummary() {
        Map<String, Object> summary = new HashMap<>();
        
        summary.put("totalEmissions", 15420);
        summary.put("totalChange", 1250);
        summary.put("changeRate", 8.8);
        summary.put("industryCount", 8);
        summary.put("resourceCount", 6);
        summary.put("dataPoints", 365);
        summary.put("lastUpdate", LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE));
        
        // 趋势数据
        List<Map<String, Object>> trends = new ArrayList<>();
        String[] months = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"};
        for (int i = 0; i < 12; i++) {
            Map<String, Object> trend = new HashMap<>();
            trend.put("month", months[i]);
            trend.put("emissions", 1200 + Math.random() * 400);
            trend.put("target", 1100 + i * 20);
            trends.add(trend);
        }
        summary.put("monthlyTrends", trends);
        
        return summary;
    }

    private Map<String, Object> generateIndustryDistribution() {
        Map<String, Object> data = new HashMap<>();
        
        List<Map<String, Object>> distribution = new ArrayList<>();
        String[] industries = {"manufacturing", "energy", "transportation", "agriculture", "construction", "services", "mining", "chemical"};
        double[] weights = {0.25, 0.20, 0.15, 0.10, 0.12, 0.08, 0.06, 0.04};
        
        for (int i = 0; i < industries.length; i++) {
            Map<String, Object> item = new HashMap<>();
            item.put("industry", industries[i]);
            item.put("percentage", Math.round(weights[i] * 100));
            item.put("emissions", Math.round(15000 * weights[i]));
            item.put("trend", Math.random() > 0.5 ? "up" : "down");
            item.put("change", Math.round((Math.random() - 0.5) * 200));
            distribution.add(item);
        }
        
        data.put("distribution", distribution);
        data.put("totalIndustries", industries.length);
        data.put("analysisDate", LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE));
        
        return data;
    }

    private Map<String, Object> generateResourceAnalysis() {
        Map<String, Object> data = new HashMap<>();
        
        List<Map<String, Object>> resources = new ArrayList<>();
        String[] resourceTypes = {"coal", "oil", "gas", "electricity", "renewable", "nuclear"};
        double[] baseValues = {3000, 2500, 2000, 1800, 800, 400};
        
        for (int i = 0; i < resourceTypes.length; i++) {
            Map<String, Object> resource = new HashMap<>();
            resource.put("type", resourceTypes[i]);
            resource.put("currentUsage", Math.round(baseValues[i] * (0.8 + Math.random() * 0.4)));
            resource.put("efficiency", Math.round((0.6 + Math.random() * 0.3) * 100));
            resource.put("carbonIntensity", Math.round(baseValues[i] * 0.1 * (0.5 + Math.random() * 0.5)));
            resource.put("renewablePercentage", resourceTypes[i].equals("renewable") ? 100 : Math.round(Math.random() * 30));
            resources.add(resource);
        }
        
        data.put("resources", resources);
        data.put("totalResources", resourceTypes.length);
        data.put("analysisDate", LocalDate.now().format(DateTimeFormatter.ISO_LOCAL_DATE));
        
        return data;
    }

    private Map<String, Object> generateDataDetails(int page, int size) {
        Map<String, Object> data = new HashMap<>();
        
        List<Map<String, Object>> records = new ArrayList<>();
        int totalRecords = 1000;
        int startIndex = (page - 1) * size;
        
        String[] industries = {"manufacturing", "energy", "transportation", "agriculture", "construction", "services", "mining", "chemical"};
        String[] resources = {"coal", "oil", "gas", "electricity", "renewable", "nuclear"};
        
        for (int i = 0; i < Math.min(size, totalRecords - startIndex); i++) {
            Map<String, Object> record = new HashMap<>();
            record.put("id", startIndex + i + 1);
            record.put("date", LocalDate.now().minusDays(i).format(DateTimeFormatter.ISO_LOCAL_DATE));
            record.put("industry", industries[i % industries.length]);
            record.put("resource", resources[i % resources.length]);
            record.put("emissions", Math.round(500 + Math.random() * 1500));
            record.put("location", "Location " + (i % 10 + 1));
            record.put("status", Math.random() > 0.8 ? "anomaly" : "normal");
            records.add(record);
        }
        
        data.put("records", records);
        data.put("totalRecords", totalRecords);
        data.put("currentPage", page);
        data.put("pageSize", size);
        data.put("totalPages", (int) Math.ceil((double) totalRecords / size));
        
        return data;
    }

    // 辅助方法
    private double getIndustryFactor(String industry) {
        Map<String, Double> factors = new HashMap<>();
        factors.put("manufacturing", 1.2);
        factors.put("energy", 1.5);
        factors.put("transportation", 1.0);
        factors.put("agriculture", 0.8);
        factors.put("construction", 1.1);
        factors.put("services", 0.6);
        factors.put("mining", 1.3);
        factors.put("chemical", 1.4);
        return factors.getOrDefault(industry, 1.0);
    }

    private double getResourceFactor(String resource) {
        Map<String, Double> factors = new HashMap<>();
        factors.put("coal", 1.5);
        factors.put("oil", 1.3);
        factors.put("gas", 1.0);
        factors.put("electricity", 0.8);
        factors.put("renewable", 0.3);
        factors.put("nuclear", 0.2);
        return factors.getOrDefault(resource, 1.0);
    }
} 