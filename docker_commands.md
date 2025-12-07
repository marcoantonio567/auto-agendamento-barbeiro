Aqui estão os principais comandos Docker divididos por categoria:

## **GerenCIAMENTO DE CONTAINERS**

```bash
# Criar e iniciar container
docker run [opções] imagem [comando]

# Listar containers
docker ps          # Containers ativos
docker ps -a       # Todos os containers

# Iniciar/parar containers
docker start nome_container
docker stop nome_container
docker restart nome_container
docker pause nome_container
docker unpause nome_container

# Remover container
docker rm nome_container
docker rm -f nome_container  # Forçar remoção

# Executar comando em container ativo
docker exec [opções] container comando
docker exec -it container /bin/bash  # Terminal interativo

# Ver logs
docker logs nome_container
docker logs -f nome_container  # Seguir logs em tempo real
```

## **IMAGENS**

```bash
# Listar imagens
docker images
docker image ls

# Baixar imagem
docker pull nome_imagem:tag

# Remover imagem
docker rmi nome_imagem
docker rmi -f nome_imagem  # Forçar remoção

# Construir imagem
docker build -t nome_imagem:tag .
docker build -f Dockerfile.dev .  # Especificar Dockerfile

# Salvar/carregar imagem
docker save imagem > arquivo.tar
docker load < arquivo.tar
```

## **VOLUMES**

```bash
# Listar volumes
docker volume ls

# Criar volume
docker volume create nome_volume

# Remover volume
docker volume rm nome_volume
docker volume prune  # Remover volumes não usados
```

## **REDES**

```bash
# Listar redes
docker network ls

# Criar rede
docker network create nome_rede

# Conectar container à rede
docker network connect rede container

# Inspecionar rede
docker network inspect nome_rede
```

## **COMANDOS ÚTEIS**

```bash
# Ver informações do sistema
docker info
docker version

# Limpar recursos não utilizados
docker system prune        # Containers, imagens, redes
docker system prune -a     # + build cache

# Inspecionar objeto
docker inspect nome_container

# Copiar arquivos
docker cp arquivo.txt container:/caminho/
docker cp container:/caminho/arquivo.txt ./

# Estatísticas em tempo real
docker stats
```

## **COMPOSE (docker-compose.yml)**

```bash
# Iniciar serviços
docker-compose up
docker-compose up -d      # Modo detached

# Parar serviços
docker-compose down
docker-compose stop

# Ver logs
docker-compose logs
docker-compose logs -f    # Seguir logs

# Listar containers do compose
docker-compose ps

# Reconstruir serviços
docker-compose build
```

## **EXEMPLOS PRÁTICOS**

```bash
# Container Nginx com port binding
docker run -d -p 8080:80 --name meu_nginx nginx

# Container MySQL com volume
docker run -d --name mysql_db \
  -e MYSQL_ROOT_PASSWORD=senha \
  -v mysql_data:/var/lib/mysql \
  mysql:8.0

# Container com terminal interativo
docker run -it ubuntu /bin/bash

# Dockerfile build e run
docker build -t minha-app:1.0 .
docker run -p 3000:3000 minha-app:1.0
```

## **OPÇÕES COMUNS DO `docker run`**

```bash
-d                    # Executar em background
--name nome           # Nome do container
-p host:container     # Mapear portas
-v host:container     # Mapear volumes
-e VAR=valor          # Variáveis de ambiente
--network nome        # Conectar à rede
--restart always      # Política de reinício
-it                   # Terminal interativo
```

Para mais detalhes sobre qualquer comando, use:
```bash
docker comando --help
```