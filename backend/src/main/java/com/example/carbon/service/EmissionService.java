package com.example.carbon.service;

import com.example.carbon.model.EmissionRecord;
import com.example.carbon.repository.EmissionRecordRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class EmissionService {

    private final EmissionRecordRepository repository;

    public EmissionService(EmissionRecordRepository repository) {
        this.repository = repository;
    }

    public Page<EmissionRecord> page(LocalDate start, LocalDate end,
                                     List<String> industries, List<String> resources, List<String> regions,
                                     int page, int size) {
        return repository.pageFilter(start, end, nullIfEmpty(industries), nullIfEmpty(resources), nullIfEmpty(regions), PageRequest.of(page, size));
    }

    public Map<String, Object> line(LocalDate start, LocalDate end, List<String> industries, List<String> resources) {
        Map<String, Object> result = new HashMap<String, Object>();
        List<Object[]> total = repository.aggregateTotalByDate(start, end);
        List<Map<String, Object>> totalList = new ArrayList<Map<String, Object>>();
        for (Object[] row : total) {
            Map<String, Object> item = new HashMap<String, Object>();
            item.put("date", row[0]);
            item.put("value", row[1]);
            totalList.add(item);
        }
        result.put("total", totalList);
        if (industries != null && !industries.isEmpty()) {
            List<Object[]> byIndustry = repository.aggregateByIndustryOverTime(start, end, industries);
            result.put("byIndustry", toSeries(byIndustry));
        }
        if (resources != null && !resources.isEmpty()) {
            List<Object[]> byResource = repository.aggregateByResourceOverTime(start, end, resources);
            result.put("byResource", toSeries(byResource));
        }
        return result;
    }

    public List<Map<String, Object>> heatmap(LocalDate start, LocalDate end, List<String> industries, List<String> resources) {
        List<Object[]> rows = repository.heatmap(start, end, nullIfEmpty(industries), nullIfEmpty(resources));
        List<Map<String, Object>> list = new ArrayList<Map<String, Object>>();
        for (Object[] r : rows) {
            Map<String, Object> item = new HashMap<String, Object>();
            item.put("industry", r[0]);
            item.put("resource", r[1]);
            item.put("value", r[2]);
            list.add(item);
        }
        return list;
    }

    public List<Map<String, Object>> groupByIndustry(LocalDate start, LocalDate end, List<String> industries) {
        List<Object[]> rows = repository.groupByIndustry(start, end, nullIfEmpty(industries));
        List<Map<String, Object>> list = new ArrayList<Map<String, Object>>();
        for (Object[] r : rows) {
            Map<String, Object> item = new HashMap<String, Object>();
            item.put("name", r[0]);
            item.put("value", r[1]);
            list.add(item);
        }
        return list;
    }

    public List<Map<String, Object>> groupByResource(LocalDate start, LocalDate end, List<String> resources) {
        List<Object[]> rows = repository.groupByResource(start, end, nullIfEmpty(resources));
        List<Map<String, Object>> list = new ArrayList<Map<String, Object>>();
        for (Object[] r : rows) {
            Map<String, Object> item = new HashMap<String, Object>();
            item.put("name", r[0]);
            item.put("value", r[1]);
            list.add(item);
        }
        return list;
    }

    @Transactional
    public void saveAll(List<EmissionRecord> records) {
        repository.saveAll(records);
    }

    private List<String> nullIfEmpty(List<String> list) {
        return (list == null || list.isEmpty()) ? null : list;
    }

    private Map<String, List<Map<String, Object>>> toSeries(List<Object[]> rows) {
        Map<String, List<Map<String, Object>>> grouped = new LinkedHashMap<String, List<Map<String, Object>>>();
        for (Object[] r : rows) {
            String key = String.valueOf(r[1]);
            List<Map<String, Object>> series = grouped.get(key);
            if (series == null) {
                series = new ArrayList<Map<String, Object>>();
                grouped.put(key, series);
            }
            Map<String, Object> point = new HashMap<String, Object>();
            point.put("date", r[0]);
            point.put("value", r[2]);
            series.add(point);
        }
        return grouped;
    }
} 