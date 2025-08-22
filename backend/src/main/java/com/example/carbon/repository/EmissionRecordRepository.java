package com.example.carbon.repository;

import com.example.carbon.model.EmissionRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDate;
import java.util.List;

public interface EmissionRecordRepository extends JpaRepository<EmissionRecord, Long> {

    @Query("select r from EmissionRecord r where r.date between :start and :end " +
            "and (:industries is null or r.industry in :industries) " +
            "and (:resources is null or r.resource in :resources) " +
            "and (:regions is null or r.region in :regions)")
    Page<EmissionRecord> pageFilter(@Param("start") LocalDate start,
                                    @Param("end") LocalDate end,
                                    @Param("industries") List<String> industries,
                                    @Param("resources") List<String> resources,
                                    @Param("regions") List<String> regions,
                                    Pageable pageable);

    @Query("select r.date as date, sum(r.emission) as total from EmissionRecord r " +
            "where r.date between :start and :end " +
            "group by r.date order by r.date asc")
    List<Object[]> aggregateTotalByDate(@Param("start") LocalDate start, @Param("end") LocalDate end);

    @Query("select r.date as date, r.industry as k, sum(r.emission) as v from EmissionRecord r " +
            "where r.date between :start and :end and r.industry in :industries " +
            "group by r.date, r.industry order by r.date asc")
    List<Object[]> aggregateByIndustryOverTime(@Param("start") LocalDate start, @Param("end") LocalDate end, @Param("industries") List<String> industries);

    @Query("select r.date as date, r.resource as k, sum(r.emission) as v from EmissionRecord r " +
            "where r.date between :start and :end and r.resource in :resources " +
            "group by r.date, r.resource order by r.date asc")
    List<Object[]> aggregateByResourceOverTime(@Param("start") LocalDate start, @Param("end") LocalDate end, @Param("resources") List<String> resources);

    @Query("select r.industry as industry, r.resource as resource, sum(r.emission) as total from EmissionRecord r " +
            "where r.date between :start and :end and r.industry in :industries and r.resource in :resources " +
            "group by r.industry, r.resource")
    List<Object[]> heatmap(@Param("start") LocalDate start, @Param("end") LocalDate end,
                           @Param("industries") List<String> industries,
                           @Param("resources") List<String> resources);

    @Query("select r.industry as k, sum(r.emission) as v from EmissionRecord r " +
            "where r.date between :start and :end and r.industry in :industries group by r.industry")
    List<Object[]> groupByIndustry(@Param("start") LocalDate start, @Param("end") LocalDate end, @Param("industries") List<String> industries);

    @Query("select r.resource as k, sum(r.emission) as v from EmissionRecord r " +
            "where r.date between :start and :end and r.resource in :resources group by r.resource")
    List<Object[]> groupByResource(@Param("start") LocalDate start, @Param("end") LocalDate end, @Param("resources") List<String> resources);
} 