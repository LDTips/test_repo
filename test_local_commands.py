import subprocess

result = subprocess.run(['docker', 'ps'], stdout=subprocess.PIPE)  #

result = result.stdout.decode('utf-8')
result = result.split('\n')
result = result[-2]
result = result.split()

# docker exec -it <container_id> <command>
print(result)
