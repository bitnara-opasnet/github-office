#!/bin/bash
################################################
# 이 스크립트는 netconf로 요청하기 위해 yang모델 파일을 request XML로 변환한다.
# yang파일을 neconf요청을 위해 xml로 변환한다.
# xml선언문과 namespace 문은 제거된다.
# 실행한 디렉토리에 xml이 저장된다.
# 이 스크립트는 개발을 위한 임시 스크립트이다.
# 2020-01-05
################################################
PATH="/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/home/bitnara/myenv/bin:/home/bitnara/myenv/bin/pyang";
echo ""
VERSION=`pyang -v`
echo "- pyang version: "$VERSION 
CWD=`pwd`
echo "- Current directory: "$CWD
YANG_SRC_DIR="/home/bitnara/eni_test/YANG/1731"
echo "- YANG source directory: "$YANG_SRC_DIR
CMD="pyang -f sample-xml-skeleton"
echo "====================================== YANG LIST ======================================"
cd $YANG_SRC_DIR
ls Cisco-IOS-XE-wireless*oper.yang
echo "======================================================================================="
if [ "$1" != "" ]; then
    YANG_FNAME="$1"
    if [ ! -f $YANG_SRC_DIR/$YANG_FNAME ]; then
        echo "No such file or directory: $YANG_FNAME"
        echo "Failed to create the xml file. Input valid file name"
        exit 1
    fi
    OUTPUT_FNAME=`echo $YANG_FNAME|awk -F "." '{print $1}'`
    OUTPUT_FNAME=$OUTPUT_FNAME".xml"
    `$CMD $YANG_SRC_DIR/$YANG_FNAME > $CWD/$OUTPUT_FNAME`
    # `$CMD $YANG_SRC_DIR/Cisco-IOS-XE-wireless-client-oper.yang > $CWD/aaa.xml`
    cd $CWD
    # XML Declaration문 제거, XML namespace 제거
    # <?xml version='1.0' encoding='UTF-8'?>
    # <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
    # 맨 앞2줄 제거,
    # 맨뒤 1줄 제거 
    sed -i '1,2d' $OUTPUT_FNAME
    sed -i '$d' $OUTPUT_FNAME
    cat $OUTPUT_FNAME
    echo "\n"
    echo 'Ouput file name: '$OUTPUT_FNAME
else
    echo "Usage: $0 {xxx.yang}"
fi