package com.example.carbon.model;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "import_logs")
public class ImportLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String filename;

    @Column(nullable = false)
    private int success;

    @Column(nullable = false)
    private int failed;

    @Column(nullable = false)
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getFilename() { return filename; }
    public void setFilename(String filename) { this.filename = filename; }
    public int getSuccess() { return success; }
    public void setSuccess(int success) { this.success = success; }
    public int getFailed() { return failed; }
    public void setFailed(int failed) { this.failed = failed; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
} 