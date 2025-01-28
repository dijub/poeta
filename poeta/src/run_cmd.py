import subprocess


class RunCMD:
    @staticmethod
    def run(cmd: str, get_output: bool = False):
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if get_output:
            # Captura a saída completa (stdout e stderr)
            stdout, stderr = process.communicate()
            if stderr:
                print(f"Error: {stderr}", end="")
            return stdout if process.returncode == 0 else None
        else:
            # Exibe saída em tempo real
            for line in process.stdout:
                print(line, end="")
            for line in process.stderr:
                print(f"Error: {line}", end="")
            process.wait()

        # Verifica se o comando falhou
        if process.returncode != 0:
            print(f"cmd failed with exit code {process.returncode}")
            return False
        return True
