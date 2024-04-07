import json
import hashlib
import time
from pathlib import Path
from PIL import Image
from pillow_heif import HeifImagePlugin # Pillow HEIF 코덱 지원을 위한 라이브러리

class FileManager():
    """
    설정 파일 및 파일 경로 등을 관리하는 기능 클래스
    """
    def __init__(self):
        """
        파일 위치 기반으로 경로 생성 후 설정 파일 확인 및 생성. 이후 INPUT, OUTPUT 폴더 경로를 확인하는 FileManager 클래스 초기화 함수
        """
        self.BASE_DIR = Path(__file__).resolve().parent
        self.SETTINGS_FILE_DIR = Path(self.BASE_DIR).joinpath("settings.json")
        self._check_settings()
        try:
            self.settings = self._load_settings()
        except:
            self.create_settings()
            print("설정 파일 오류! - 설정 파일 로딩 실패\n설정 파일을 초기화합니다.\n다시 실행해주세요")
            exit()

        self.INPUT_FILES_DIR = self.settings["SETTINGS"]["INPUT_FILES_DIR"]
        self.OUTPUT_FILES_DIR = self.settings["SETTINGS"]["OUTPUT_FILES_DIR"]

        self._check_dir()

    def _check_settings(self):
        """
        경로 내 설정 파일 확인 후 없다면 create_settings 함수를 실행하는 클래스 내부 함수
        """
        if not Path(self.SETTINGS_FILE_DIR).exists(): self.create_settings()

    def create_settings(self):
        """
        설정 파일을 setting.json 파일로 생성하는 함수
        """
        settings = {
            "SETTINGS": {
                "INPUT_FILES_DIR" : f"{Path(self.BASE_DIR).joinpath('INPUT').resolve()}",
                "OUTPUT_FILES_DIR" : f"{Path(self.BASE_DIR).joinpath('OUTPUT').resolve()}",
                "FILENAME_HASHING" : True,
                "DELETE_METADATA" : True,
                "CONVERT_TO_JPEG" : False,
                "COMPRESS_JPEG" : False,
                "DELETE_ORIGINAL_IMAGE" : False,
            }
        }

        with open(self.SETTINGS_FILE_DIR, 'w') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)

    def _load_settings(self):
        """
        설정 파일을 불러오고 설정값을 받아오는 클래스 내부 함수
        """
        with open(self.SETTINGS_FILE_DIR, 'r') as file:
            settings = json.load(file)
        return settings

    def _check_dir(self):
        """
        INPUT, OUTPUT 폴더 여부를 확인하는 클래스 내부 함수
        """
        if not Path(self.INPUT_FILES_DIR).exists(): Path(self.INPUT_FILES_DIR).mkdir(parents=False, exist_ok=True), print("Error! No Files")
        if not Path(self.OUTPUT_FILES_DIR).exists(): Path(self.OUTPUT_FILES_DIR).mkdir(parents=False, exist_ok=True)

class Anonymizer():
    """
    이미지 처리 관련 기능 클래스
    """
    def __init__(self):
        """
        FileManager 클래스 객체 생성 및 지원 파일 설정 등의 Anonymizer 클래스 초기화 함수
        """
        self.file_manager = FileManager()
        self.file_ext = ("*.jpg", "*.jpeg", "*.png", "*.heif", "*.heic", "*.heix")
        self.img_list = []
        self.dir_file_cnt = len(list(Path(self.file_manager.INPUT_FILES_DIR).glob("*")))

    def make_img_list(self):
        """
        폴더 내 이미지 처리 지원 파일을 구분해서 처리할 이미지 리스트를 만드는 함수
        """
        for files in self.file_ext:
            self.img_list.extend(Path(self.file_manager.INPUT_FILES_DIR).glob(files))

        dir_file_cnt = len(list(Path(self.file_manager.INPUT_FILES_DIR).glob("*")))
        vaild_file_cnt = len(self.img_list)
        print(f"전체 파일 {dir_file_cnt}개 / 미지원 파일 {dir_file_cnt - vaild_file_cnt}개 확인\n")

    def _get_save_dir(self, img_dir):
        """
        이미지 파일 입력 경로를 받아서 파일 이름을 해싱하고 이미지 파일을 저장할 출력 경로를 return 해주는 클래스 내부 함수 
        Args:
            img_dir (str) : 이미지 파일 경로
        """
        file_name = Path(img_dir).stem
        file_suffix = Path(img_dir).suffix
        save_dir = Path(self.file_manager.OUTPUT_FILES_DIR)

        try:
            if anonymizer.file_manager.settings["SETTINGS"]["FILENAME_HASHING"] == True:
                # 해싱 옵션 True
                hashed_name = hashlib.sha256(file_name.encode()).hexdigest() + file_suffix
                return save_dir.joinpath(hashed_name)
            elif anonymizer.file_manager.settings["SETTINGS"]["FILENAME_HASHING"] == False:
                # 해싱 옵션 False
                return save_dir.joinpath(file_name + file_suffix)
            else:
                self.file_manager.create_settings()
                print("설정 파일 오류! - FILENAME_HASHING 옵션\n설정 파일을 초기화합니다.")
                raise
        except:
            print("이미지 저장 경로 생성 중 오류 발생! 다시 실행해주세요")
            exit()

    def process_img(self):
        """
        이미지 처리가 이루어지는 함수 
        """
        start_time = time.time() # 처리 시간 계산용 시작 타이머
        img_cnt = len(self.img_list)
        processing_img_num = 1

        for img_dir in self.img_list: # 전체 이미지 처리 for 문
            print(f"({processing_img_num}/{img_cnt}) - {Path(img_dir).stem + Path(img_dir).suffix} 처리 중...", end="")

            try:
                if anonymizer.file_manager.settings["SETTINGS"]["CONVERT_TO_JPEG"] == True:
                    # JPEG 변환 옵션 True
                    # 기존 이미지 경로 대신 JPEG으로 변환 후 이미지가 저장될 출력 경로 내 새 경로 지정
                    img_dir = self._save_to_jpeg(img_dir)
                elif anonymizer.file_manager.settings["SETTINGS"]["CONVERT_TO_JPEG"] == False:
                    # JPEG 변환 옵션 False
                    pass
                else:
                    self.file_manager.create_settings()
                    print("설정 파일 오류! - CONVERT_TO_JPEG 옵션\n설정 파일을 초기화합니다.")
                    raise
            except:
                print("다시 실행해주세요")
                exit()

            try:
                if anonymizer.file_manager.settings["SETTINGS"]["DELETE_METADATA"] == True:
                    # 메타데이터 삭제 옵션 True
                    self._delete_img_exif(img_dir)
                elif anonymizer.file_manager.settings["SETTINGS"]["DELETE_METADATA"] == False:
                    # 메타데이터 삭제 옵션 False
                    self._maintain_img_exif(img_dir)
                else:
                    self.file_manager.create_settings()
                    print("설정 파일 오류! - DELETE_METADATA 옵션\n설정 파일을 초기화합니다.")
                    raise
            except:
                print("이미지 처리 중 오류 발생! 다시 실행해주세요")
                exit()
            
            print(f"\r({processing_img_num}/{img_cnt}) - {Path(img_dir).stem + Path(img_dir).suffix} 처리 완료..!")

            try:
                if anonymizer.file_manager.settings["SETTINGS"]["DELETE_ORIGINAL_IMAGE"] == True:
                    # 원본 이미지 삭제 옵션 True
                    # 원본 이미지 경로 파일 삭제
                    Path(img_dir).unlink(missing_ok=True)
                elif anonymizer.file_manager.settings["SETTINGS"]["DELETE_ORIGINAL_IMAGE"] == False:
                    # 원본 이미지 삭제 옵션 False
                    pass
                else:
                    self.file_manager.create_settings()
                    print("설정 파일 오류! - DELETE_ORIGINAL_IMAGE 옵션\n설정 파일을 초기화합니다.")
                    raise
            except:
                pass
            
            if anonymizer.file_manager.settings["SETTINGS"]["CONVERT_TO_JPEG"] == True:
                # JPEG 변환 옵션 True
                # 최상단 동일한 if 문에서 옵션 정상 여부 확인했기 때문에 try except 사용하지 않음
                # 모든 이미지 처리 후 출력 경로 내 새로 만들어졌던 JPEG 이미지 삭제
                Path(img_dir).unlink(missing_ok=True)
            elif anonymizer.file_manager.settings["SETTINGS"]["CONVERT_TO_JPEG"] == False:
                pass

            processing_img_num += 1
        end_time = time.time() # 처리 시간 계산용 종료 타이머
        print(f"\n전체 이미지 처리 완료 - (처리 시간 {round((end_time - start_time), 1)}초)")

    def _delete_img_exif(self, img_dir):
        """
        이미지 파일 경로를 받아 exif 데이터를 삭제 후 이미지를 저장하는 클래스 내부 함수
        Args:
            img_dir (str) : 이미지 파일 경로
        """
        img = Image.open(img_dir)

        img_exif = img.getexif()
        
        img.info["xmp"] = None

        for tag, value in img_exif.items():
            if tag != 274: # 사진 방향 데이터 (Orientation) 유지
                del img_exif[tag]

        try:
            if anonymizer.file_manager.settings["SETTINGS"]["COMPRESS_JPEG"] == True:
                # JPEG 용량 압축 옵션 True
                if Path(img_dir).suffix == (".JPG" or ".JPEG" or ".jpg" or ".jpeg"):
                    # JPEG 코덱 이미지의 경우 web_low quality로 저장
                    img.save(self._get_save_dir(img_dir), exif=img_exif, quality="web_low")
                else:
                    # JPEG 코덱 이외의 이미지의 경우 압축하지 않음
                    img.save(self._get_save_dir(img_dir), exif=img_exif)
            elif anonymizer.file_manager.settings["SETTINGS"]["COMPRESS_JPEG"] == False:
                # JPEG 용량 압축 옵션 False
                img.save(self._get_save_dir(img_dir), exif=img_exif)
            else:
                self.file_manager.create_settings()
                print("설정 파일 오류! - COMPRESS_JPEG 옵션\n설정 파일을 초기화합니다.")
                raise
        except:
            print("이미지 저장 중 오류 발생! 다시 실행해주세요")
            exit()

    def _maintain_img_exif(self, img_dir):
        """
        이미지 파일 경로를 받아 exif 데이터를 유지 후 이미지를 저장하는 클래스 내부 함수
        Args:
            img_dir (str) : 이미지 파일 경로
        """
        img = Image.open(img_dir)

        try:
            if anonymizer.file_manager.settings["SETTINGS"]["COMPRESS_JPEG"] == True:
                # JPEG 용량 압축 옵션 True
                if Path(img_dir).suffix == (".JPG" or ".JPEG" or ".jpg" or ".jpeg"):
                    # JPEG 코덱 이미지의 경우 web_low quality로 저장
                    img.save(self._get_save_dir(img_dir), exif=img.getexif(), quality="web_low")
                else:
                    # JPEG 코덱 이외의 이미지의 경우 압축하지 않음
                    img.save(self._get_save_dir(img_dir), exif=img.getexif())
            elif anonymizer.file_manager.settings["SETTINGS"]["COMPRESS_JPEG"] == False:
                # JPEG 용량 압축 옵션 False
                img.save(self._get_save_dir(img_dir), exif=img.getexif())
            else:
                self.file_manager.create_settings()
                print("설정 파일 오류! - COMPRESS_JPEG 옵션\n설정 파일을 초기화합니다.")
                raise
        except:
            print("이미지 저장 중 오류 발생!\n다시 실행해주세요")
            exit()

    def _save_to_jpeg(self, img_dir):
        """
        이미지 파일 경로를 받아 출력 경로에 새로운 JPEG 이미지를 생성(JPEG으로 변환)하는 클래스 내부 함수
        Args:
            img_dir (str) : 이미지 파일 경로
        """
        img = Image.open(img_dir)
        jpeg_dir = Path(self.file_manager.OUTPUT_FILES_DIR).joinpath(Path(img_dir).stem + ".JPG")
        img.save(jpeg_dir)

        try:
            if anonymizer.file_manager.settings["SETTINGS"]["DELETE_ORIGINAL_IMAGE"] == True:
                # 원본 이미지 삭제 옵션 True
                # 원본 이미지 경로 파일 삭제
                Path(img_dir).unlink(missing_ok=True)
            elif anonymizer.file_manager.settings["SETTINGS"]["DELETE_ORIGINAL_IMAGE"] == False:
                # 원본 이미지 삭제 옵션 False
                pass
            else:
                self.file_manager.create_settings()
                print("설정 파일 오류! - DELETE_ORIGINAL_IMAGE 옵션\n설정 파일을 초기화합니다.")
                raise
        except:
            pass

        return jpeg_dir

anonymizer = Anonymizer()
anonymizer.make_img_list()
anonymizer.process_img()