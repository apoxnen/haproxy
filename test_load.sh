set -B
for i in {1..1000}; do
  curl localhost:8000
  echo
  sleep 1
done
