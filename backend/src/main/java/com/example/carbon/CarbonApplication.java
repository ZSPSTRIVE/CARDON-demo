package com.example.carbon;

import com.example.carbon.model.Role;
import com.example.carbon.model.User;
import com.example.carbon.repository.UserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import java.util.Collections;

@SpringBootApplication
public class CarbonApplication {

    public static void main(String[] args) {
        SpringApplication.run(CarbonApplication.class, args);
    }

    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public CommandLineRunner seedAdmin(UserRepository userRepository, BCryptPasswordEncoder encoder) {
        return args -> {
            if (!userRepository.findByUsername("admin").isPresent()) {
                User admin = new User();
                admin.setUsername("admin");
                admin.setPassword(encoder.encode("admin123"));
                admin.setRoles(Collections.singleton(Role.ADMIN));
                userRepository.save(admin);
                System.out.println("[INIT] Created default admin: admin / admin123");
            }
        };
    }
} 