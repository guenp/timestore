docker run --rm -d --name timescaledb -e POSTGRES_PASSWORD=ts -p 5432:5432 timescale/timescaledb
docker run -d -p 8081:8081 --link timescaledb:db -e DATABASE_URL="postgres://postgres:ts@db:5432/postgres?sslmode=disable" sosedoff/pgweb
docker run -d -p 3000:3000 --link timescaledb:db grafana/grafana
