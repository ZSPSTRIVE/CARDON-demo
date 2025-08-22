CREATE TABLE IF NOT EXISTS users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_roles (
  user_id BIGINT NOT NULL,
  role VARCHAR(32) NOT NULL,
  CONSTRAINT fk_user_roles_user FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS emission_records (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  date DATE NOT NULL,
  industry VARCHAR(64) NOT NULL,
  resource VARCHAR(64) NOT NULL,
  region VARCHAR(64) NOT NULL,
  emission DECIMAL(18,4) NOT NULL,
  INDEX idx_date (date),
  INDEX idx_industry (industry),
  INDEX idx_resource (resource),
  INDEX idx_region (region)
);

CREATE TABLE IF NOT EXISTS import_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  filename VARCHAR(255) NOT NULL,
  success INT NOT NULL,
  failed INT NOT NULL,
  created_at DATETIME NOT NULL
);

-- 示例数据（YYYY-MM-01 表示月份）
INSERT INTO emission_records (date, industry, resource, region, emission) VALUES
('2022-01-01','能源','煤炭','全国',12345.67),
('2022-02-01','能源','煤炭','全国',11500.00),
('2022-01-01','制造','电力','华东',4300.12),
('2022-01-01','交通','汽油','华北',2200.50); 