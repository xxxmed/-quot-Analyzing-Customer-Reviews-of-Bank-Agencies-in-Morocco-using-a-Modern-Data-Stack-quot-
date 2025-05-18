CREATE DATABASE bd_staging;
CREATE DATABASE bd_decisionnelle;
ALTER DATABASE bd_staging OWNER TO zakaria;
ALTER DATABASE bd_decisionnelle OWNER TO zakaria;
GRANT ALL PRIVILEGES ON DATABASE bd_staging TO zakaria;
GRANT ALL PRIVILEGES ON DATABASE bd_decisionnelle TO zakaria;
