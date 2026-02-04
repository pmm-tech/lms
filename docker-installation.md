**Step 1:** Clone the repo

```
$ git clone https://github.com/frappe/lms.git

$ cd lms

$ cd docker
```

**Step 2:** Run docker-compose

```
$ docker-compose up
```

**Step 3:** Visit the website at http://localhost:8000/

You'll have to go through the setup wizard to setup the website for the first time you access it. Login using the following credentials to complete the setup wizard.

```
Username: Administrator
password: admin
```

TODO: Explain how to load sample data

## Stopping the server

Press `ctrl+c` in the terminal to stop the server. You can also run `docker-compose down` in another terminal to stop it.

To completely reset the instance, do the following:

```
$ docker-compose down --volumes
$ docker-compose up
```

---

## Production deployment with Docker Compose

Use the production compose stack when you want to run Frappe LMS on a server with MariaDB, Redis, and all app services (backend, frontend, workers, scheduler) in containers. The image used by default is `ghcr.io/frappe/lms:stable`. You can override it with your own built image (e.g. from the [Build workflow](.github/workflows/build.yml)).

**Prerequisites:** Docker and Docker Compose v2 on the server.

**Step 1:** Clone the repo and go to the `docker` directory

```
$ git clone https://github.com/frappe/lms.git
$ cd lms/docker
```

**Step 2:** Create production env file

Copy the example env file and set at least the database password:

```
$ cp env.production.example .env
```

Edit `.env` and set a strong `DB_PASSWORD`. Optionally set `CUSTOM_IMAGE` and `CUSTOM_TAG` if you use your own image (e.g. `CUSTOM_IMAGE=ghcr.io/your-org/lms`, `CUSTOM_TAG=v1.0.0`).

**Step 3:** Start the production stack

```
$ docker compose -f docker-compose.production.yml --env-file .env up -d
```

This starts MariaDB, Redis, and all Frappe/LMS services. The web frontend listens on port **8080** by default (override with `HTTP_PUBLISH_PORT` in `.env`).

**Step 4:** Create a site and install the LMS app

Replace `lms.example.com` with your site hostname (or use your server IP / host). The hostname must match how you will access the site (or set `FRAPPE_SITE_NAME_HEADER` in `.env`).

```
$ docker compose -f docker-compose.production.yml exec backend bench new-site lms.example.com \
  --mariadb-root-password "$(grep DB_PASSWORD .env | cut -d= -f2)" \
  --admin-password admin \
  --install-app lms
```

Set a strong admin password in production instead of `admin`.

**Step 5:** Access the app

Open `http://your-server:8080` (or your domain if you put a reverse proxy in front). Use the admin username and password you set in Step 4.

**Optional**

- **Reverse proxy (HTTPS):** Put Traefik, Nginx, or another reverse proxy in front of the `frontend` service (port 8080). Use `UPSTREAM_REAL_IP_*` and `FRAPPE_SITE_NAME_HEADER` in `.env` if the site is resolved by a different host header.
- **Production settings:** After creating the site, you can set `block_endpoints` and other options, e.g.  
  `docker compose -f docker-compose.production.yml exec backend bench --site lms.example.com set-config block_endpoints 1`

**Stopping the production stack**

```
$ docker compose -f docker-compose.production.yml --env-file .env down
```

To remove data volumes as well: `docker compose -f docker-compose.production.yml --env-file .env down --volumes`.
