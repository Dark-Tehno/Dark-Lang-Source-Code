# Copyright 2026 Dark.Tehno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import requests
import zipfile
import io
import os
import shutil


class DarkPackageManager:
    """
    Менеджер пакетов для языка Dark (dpm).
    Управляет установкой, удалением и листингом расширений из GitHub.
    """
    GITHUB_API_URL = "https://api.github.com/search/repositories"
    PACKAGE_PREFIX = "Dark_"

    def __init__(self, args):
        self.denv_path = os.environ.get('DARK_ENV')
        if not self.denv_path:
            print("Ошибка: Менеджер пакетов 'dpm' должен быть запущен внутри активного окружения 'denv'.")
            print("Активируйте окружение командой: source <env_name>/bin/activate")
            sys.exit(1)

        self.extensions_dir = os.path.join(self.denv_path, 'dark_extensions')
        self.args = args

    def run(self):
        """Запускает выполнение команды."""
        if not self.args or self.args[0] in ('--help', 'help'):
            self.show_help()
            return

        command = self.args[0]
        command_args = self.args[1:]

        if command == 'install':
            if not command_args:
                if os.path.exists('requirements.txt'):
                    with open('requirements.txt', 'r') as f:
                        for line in f:
                            package_name = line.strip()
                            if package_name:
                                self.install_package(package_name)
                else:
                    print("Ошибка: файл 'requirements.txt' не найден.")
                    self.show_help()
                    sys.exit(1)
            else:
                if os.path.exists(command_args):
                    with open(command_args, 'r') as f:
                        for line in f:
                            package_name = line.strip()
                            if package_name:
                                self.install_package(package_name)
                else:
                    print(f"Ошибка: файл '{command_args}' не найден.")
            for package_name in command_args:
                self.install_package(package_name)
        elif command == 'uninstall':
            if not command_args:
                print("Ошибка: команда 'uninstall' требует имя пакета.")
                self.show_help()
                sys.exit(1)
            for package_name in command_args:
                self.uninstall_package(package_name)
        elif command == 'list':
            self.list_packages()
        elif command == 'freeze':
            if command_args:
                self.freeze_packages(requirements=command_args[0])
            else:
                self.freeze_packages()
        elif command == 'doctor':
            self.doctor_check()
        elif command == 'update':
            if not command_args:
                print("Ошибка: команда 'update' требует имя пакета.")
                self.show_help()
                sys.exit(1)
            for package_name in command_args:
                self.update_package(package_name)
        else:
            print(f"Неизвестная команда: '{command}'")
            self.show_help()
            sys.exit(1)

    def install_package(self, package_name):
        """Находит и устанавливает пакет из GitHub."""
        print(f"Поиск пакета '{package_name}'...")
        
        repo_name = f"{self.PACKAGE_PREFIX}{package_name}"
        params = {'q': f'{repo_name} in:name'}
        
        try:
            response = requests.get(self.GITHUB_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if not data['items']:
                print(f"Ошибка: Пакет '{package_name}' (репозиторий '{repo_name}') не найден на GitHub.")
                return  

            repositories = [
                repo for repo in data['items'] if repo['name'] == repo_name
            ]

        
            if not repositories:
                print(f"Ошибка: Пакет '{package_name}' (репозиторий '{repo_name}') не найден на GitHub.")
                return
            
            if len(repositories) == 1:
                repo_data = repositories[0]
            else:
                print(f"Найдено несколько пакетов '{package_name}'. Выберите, какой установить:")
                for i, repo in enumerate(repositories):
                    print(f"  {i + 1}) {repo['full_name']} - {repo.get('description', 'Нет описания')}")
                
                while True:
                    try:
                        choice = input(f"Введите номер (1-{len(repositories)}): ")
                        choice_index = int(choice) - 1
                        if 0 <= choice_index < len(repositories):
                            repo_data = repositories[choice_index]
                            break
                        else:
                            print("Неверный номер. Попробуйте еще раз.")
                    except ValueError:
                        print("Пожалуйста, введите число.")
                    except (KeyboardInterrupt, EOFError):
                        print("\nУстановка отменена.")
                        return
            repo_full_name = repo_data['full_name']
            print(f"Найден репозиторий: {repo_full_name}")

            zip_url = f"https://github.com/{repo_full_name}/archive/refs/heads/main.zip"
            print(f"Скачивание с {zip_url}...")
            zip_response = requests.get(zip_url)
            zip_response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                root_folder_in_zip = z.namelist()[0]
                
                package_folder_in_zip = None
                for name in z.namelist():
                    parts = name.replace('\\', '/').split('/')
                    if len(parts) > 2 and parts[1] == package_name and parts[2] == '__init__.py':
                        package_folder_in_zip = f"{parts[0]}/{parts[1]}/"
                        break
                
                if not package_folder_in_zip:
                    print(f"Ошибка: не удалось найти папку пакета '{package_name}' внутри архива.")
                    return

                print(f"Распаковка пакета '{package_name}' в {self.extensions_dir}...")
                target_path = os.path.join(self.extensions_dir, package_name)
                if os.path.exists(target_path):
                    print(f"Предупреждение: пакет '{package_name}' уже существует. Переустановка...")
                    shutil.rmtree(target_path)

                for member in z.infolist():
                    if member.filename.startswith(package_folder_in_zip) and not member.is_dir():
                        source = z.open(member)
                        relative_path = member.filename.split('/', 1)[1] 
                        target_file = os.path.join(self.extensions_dir, relative_path)
                        os.makedirs(os.path.dirname(target_file), exist_ok=True)
                        with open(target_file, "wb") as dest:
                            shutil.copyfileobj(source, dest)

            print(f"Пакет '{package_name}' успешно установлен.")

        except requests.RequestException as e:
            print(f"Ошибка сети при установке пакета: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

    def uninstall_package(self, package_name):
        """Удаляет установленный пакет."""
        package_path = os.path.join(self.extensions_dir, package_name)
        if not os.path.isdir(package_path):
            print(f"Пакет '{package_name}' не установлен.")
            return
        
        try:
            shutil.rmtree(package_path)
            print(f"Пакет '{package_name}' успешно удален.")
        except OSError as e:
            print(f"Ошибка при удалении пакета '{package_name}': {e}")

    def list_packages(self):
        """Показывает список установленных пакетов."""
        print(f"Пакеты, установленные в '{self.denv_path}':")
        if not os.path.exists(self.extensions_dir) or not os.listdir(self.extensions_dir):
            print("  (нет установленных пакетов)")
            return
        
        for item in sorted(os.listdir(self.extensions_dir)):
            if os.path.isdir(os.path.join(self.extensions_dir, item)):
                print(f"  - {item}")
    
    def freeze_packages(self, requirements="requirements.txt"):
        """Сохраняет список установленных пакетов в requirements.txt."""
        with open(requirements, 'w') as f:
            for item in sorted(os.listdir(self.extensions_dir)):
                if os.path.isdir(os.path.join(self.extensions_dir, item)):
                    f.write(f"{item}\n")
        print(f"Список установленных пакетов сохранен в '{requirements}'.")

    
    def doctor_check(self):
        """Проверяет наличие необходимых пакетов."""
        print("Проверка наличия необходимых пакетов...")
        if not os.path.exists(self.extensions_dir):
            print(f"  Директория расширений '{self.extensions_dir}' не существует. Создание...")
            os.makedirs(self.extensions_dir)
        else:
            print(f"  Директория расширений '{self.extensions_dir}' существует.")

        if not os.access(self.extensions_dir, os.W_OK):
            print(f"  Ошибка: Нет прав на запись в директорию расширений '{self.extensions_dir}'.")
        else:
            print(f"  Права на запись в директорию расширений '{self.extensions_dir}' в порядке.")

        try:
            req = requests.get("https://api.github.com")
            req.raise_for_status()
            print("  Подключение к GitHub успешно.")
        except requests.exceptions.RequestException as e:
            print(f"  Ошибка: Не удалось подключиться к GitHub. Проверьте ваше интернет-соединение. ({e})")
            sys.exit(1)

    
    def update_package(self, package_name):
        """Обновляет пакет."""
        print(f"Обновление пакета '{package_name}'...")
        package_path = os.path.join(self.extensions_dir, package_name)
        if not os.path.isdir(package_path):
            print(f"Пакет '{package_name}' не установлен. Используйте 'dark --dpm install {package_name}' для установки.")
            return
        
        self.uninstall_package(package_name)
        self.install_package(package_name)
        

        print("Проверка завершена.") 

    def show_help(self):
        """Показывает справку по использованию."""
        print("""
Менеджер пакетов Dark (dpm)

Использование: dark --dpm <команда> [аргументы]

Команды:
  install <имя_пакета>...       Установить один или несколько пакетов из GitHub.
                                 Ищет репозитории с именем 'Dark_<имя_пакета>'.
  uninstall <имя_пакета>...     Удалить один или несколько установленных пакетов.
  list                          Показать список всех установленных пакетов.
  help                          Показать это сообщение.
  freeze <фаил_зависимостей>    Сохранить список установленных пакетов в 'requirements.txt' или в указаном файле.
  doctor                        Проверить целостность окружения.
  update <имя_пакета>           Обновить пакет.
""")
