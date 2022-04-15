import pyang
import os
import subprocess

def yangtoxml(parent_dir, yang_dir, filename, file_dir=''):
    # pyang 버전
    VERSION = pyang.__version__
    print("- pyang version: ", VERSION)

    #현재 디렉토리
    CWD = os.getcwd()
    print("- Current directory: ", CWD)

    # yang 파일이 위치한 디렉토리
    YANG_DIR = yang_dir
    print("- YANG source directory: ", YANG_DIR)

    # yang 파일이 참조할 상위 디렉토리
    PARENT_DIR = parent_dir

    # yang 파일과 파일명이 동일한 xml 파일 생성
    YANG_FNAME = filename
    OUTPUT_FNAME = YANG_FNAME.split('.')[0] + ".xml"

    # xml 파일이 저장될 디렉토리, 없으면 현재 디렉토리에 저장
    if file_dir:
        OUTPUT_DIR = file_dir + '/'
    else: 
        OUTPUT_DIR = CWD + '/'

    # subporcess를 이용해 command 실행
    # -p 옵션으로 참조할 상위 디렉토리 경로 설정 
    try:
        # subprocess.check_output(command.split(' '), universal_newlines=True)
        result = subprocess.check_output(['pyang', '-p', PARENT_DIR, '-f', 'sample-xml-skeleton', YANG_DIR+'/'+YANG_FNAME], universal_newlines=True)

        """
        pyang -p /home/bitnara/netconftest/yang -f sample-xml-skeleton 
        /home/bitnara/netconftest/yang/vendor/cisco/xe/1731/Cisco-IOS-XE-process-cpu-oper.yang
        """
        # 앞 두줄, 뒤 한줄 제거
        result_rm = '\n'.join(result.split('\n')[2:-2])
        print(result_rm)

        #xml 파일로 저장
        with open(OUTPUT_DIR + OUTPUT_FNAME, "wb") as f:
            f.write(result_rm.encode())
            print(OUTPUT_FNAME," creation successful")

    except Exception as e:
        print(e)

# yangtoxml(parent_dir= '/home/bitnara/netconftest/yang', 
#           yang_dir='/home/bitnara/netconftest/yang/vendor/cisco/xe/1731', 
#           filename='openconfig-routing-policy.yang', 
#           file_dir='/home/bitnara/netconftest/xmldata/standard')

# yangtoxml(parent_dir= '/home/bitnara/netconftest/yang', 
#           yang_dir='/home/bitnara/netconftest/yang/standard/ietf/RFC', 
#           filename='ietf-routing-policy.yang', 
#           file_dir='/home/bitnara/netconftest/xmldata/xe-1731')

yangtoxml(parent_dir= '/home/bitnara/netconftest/yang', 
          yang_dir='/home/bitnara/netconftest/', 
          filename='Cisco-IOS-XE-process-cpu-oper.yang', 
          file_dir='/home/bitnara/netconftest/')