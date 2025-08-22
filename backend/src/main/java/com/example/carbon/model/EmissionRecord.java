package com.example.carbon.model;

import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "emission_records",
        indexes = {
                @Index(name = "idx_date", columnList = "date"),
                @Index(name = "idx_industry", columnList = "industry"),
                @Index(name = "idx_resource", columnList = "resource"),
                @Index(name = "idx_region", columnList = "region")
        })
public class EmissionRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private LocalDate date; // 统计日期（按日或按月切换，初期按月 YYYY-MM-01）

    @Column(nullable = false, length = 64)
    private String industry; // 行业

    @Column(nullable = false, length = 64)
    private String resource; // 资源

    @Column(nullable = false, length = 64)
    private String region; // 地区

    @Column(nullable = false, precision = 18, scale = 4)
    private BigDecimal emission; // 排放量（吨 CO2e）

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public LocalDate getDate() { return date; }
    public void setDate(LocalDate date) { this.date = date; }
    public String getIndustry() { return industry; }
    public void setIndustry(String industry) { this.industry = industry; }
    public String getResource() { return resource; }
    public void setResource(String resource) { this.resource = resource; }
    public String getRegion() { return region; }
    public void setRegion(String region) { this.region = region; }
    public BigDecimal getEmission() { return emission; }
    public void setEmission(BigDecimal emission) { this.emission = emission; }
} 