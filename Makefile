docker-image:
	docker buildx build --platform linux/amd64 -t abbrbot .
	docker tag abbrbot ghcr.io/askvrtsv/abbrbot:latest
	docker push ghcr.io/askvrtsv/abbrbot:latest
