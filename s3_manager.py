"""
s3_manager.py
S3 파일 업로드 및 관리 유틸리티
"""

import os
import boto3
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv


class S3Manager:
    """S3 파일 업로드 및 관리 클래스"""
    
    def __init__(self, bucket_name=None, region=None):
        """
        S3Manager 초기화
        
        Args:
            bucket_name (str, optional): S3 버킷 이름. None이면 .env에서 읽음
            region (str, optional): AWS 리전. None이면 .env에서 읽음
        """
        # .env 파일 로드
        load_dotenv()
        
        # 환경 변수에서 설정 읽기
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME')
        self.region = region or os.getenv('AWS_REGION', 'ap-northeast-2')
        self.reports_prefix = os.getenv('S3_REPORTS_PREFIX', 'reports/')
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME이 설정되지 않았습니다. .env 파일을 확인하세요.")
        
        # S3 클라이언트 초기화
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            print(f"✅ S3 클라이언트 초기화 완료: {self.bucket_name} (리전: {self.region})")
        except NoCredentialsError:
            raise ValueError("AWS 자격 증명을 찾을 수 없습니다. .env 파일의 AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY를 확인하세요.")
    
    def upload_file(self, local_path, s3_key=None, metadata=None):
        """
        파일을 S3에 업로드
        
        Args:
            local_path (str): 업로드할 로컬 파일 경로
            s3_key (str, optional): S3에 저장될 키(경로). None이면 자동 생성
            metadata (dict, optional): 파일 메타데이터
        
        Returns:
            str: 업로드된 파일의 S3 URL (성공시), None (실패시)
        """
        if not os.path.exists(local_path):
            print(f"❌ 파일을 찾을 수 없습니다: {local_path}")
            return None
        
        # S3 키 생성 (지정되지 않은 경우)
        if s3_key is None:
            filename = os.path.basename(local_path)
            s3_key = self.generate_s3_key(filename)
        
        try:
            # 메타데이터 설정 (ASCII만 허용)
            extra_args = {}
            if metadata:
                # 한글이 포함된 메타데이터를 안전하게 처리
                safe_metadata = self._sanitize_metadata(metadata)
                if safe_metadata:
                    extra_args['Metadata'] = safe_metadata
            
            # ContentType 자동 설정 (PDF)
            if local_path.endswith('.pdf'):
                extra_args['ContentType'] = 'application/pdf'
            
            # 파일 업로드
            print(f"📤 S3 업로드 시작: {local_path} → s3://{self.bucket_name}/{s3_key}")
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # S3 URL 생성
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            print(f"✅ S3 업로드 완료!")
            print(f"📍 S3 URL: {s3_url}")
            
            return s3_url
            
        except ClientError as e:
            print(f"❌ S3 업로드 실패: {e}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return None
    
    def generate_s3_key(self, filename, include_timestamp=True):
        """
        S3 키(경로) 자동 생성
        
        Args:
            filename (str): 파일 이름
            include_timestamp (bool): 타임스탬프 포함 여부
        
        Returns:
            str: 생성된 S3 키
        """
        if include_timestamp:
            # 타임스탬프 추가 (예: report_20251019_143022.pdf)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(filename)
            filename_with_timestamp = f"{name}_{timestamp}{ext}"
        else:
            filename_with_timestamp = filename
        
        # reports/ 접두사 추가
        s3_key = f"{self.reports_prefix}{filename_with_timestamp}"
        return s3_key
    
    def delete_local_file(self, local_path):
        """
        로컬 파일 삭제
        
        Args:
            local_path (str): 삭제할 로컬 파일 경로
        
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                print(f"🗑️  로컬 파일 삭제 완료: {local_path}")
                return True
            else:
                print(f"⚠️  파일이 존재하지 않음: {local_path}")
                return False
        except Exception as e:
            print(f"❌ 파일 삭제 실패: {e}")
            return False
    
    def _sanitize_metadata(self, metadata):
        """
        S3 메타데이터에서 non-ASCII 문자 제거
        
        Args:
            metadata (dict): 원본 메타데이터
        
        Returns:
            dict: ASCII만 포함된 메타데이터
        """
        safe_metadata = {}
        for key, value in metadata.items():
            try:
                # ASCII로 인코딩 가능한지 확인
                key.encode('ascii')
                value.encode('ascii')
                safe_metadata[key] = value
            except UnicodeEncodeError:
                # non-ASCII 문자가 있으면 제거 또는 대체
                safe_key = key.encode('ascii', 'ignore').decode('ascii')
                safe_value = value.encode('ascii', 'ignore').decode('ascii')
                if safe_key and safe_value:
                    safe_metadata[safe_key] = safe_value
                else:
                    print(f"⚠️  메타데이터 제외 (non-ASCII): {key}={value}")
        return safe_metadata
    
    def check_connection(self):
        """
        S3 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ S3 버킷 연결 성공: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ S3 버킷을 찾을 수 없음: {self.bucket_name}")
            elif error_code == '403':
                print(f"❌ S3 버킷 접근 권한 없음: {self.bucket_name}")
            else:
                print(f"❌ S3 연결 실패: {e}")
            return False


# 테스트 코드
if __name__ == "__main__":
    print("🧪 S3Manager 테스트 시작...\n")
    
    try:
        # S3Manager 초기화
        s3_manager = S3Manager()
        
        # 연결 테스트
        print("\n📡 S3 연결 테스트...")
        s3_manager.check_connection()
        
        print("\n✅ 모든 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")