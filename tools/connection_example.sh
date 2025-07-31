#!/bin/bash

# IBM COS コネクションの追加
orchestrate connections add -a icos

# 接続設定の構成
orchestrate connections configure -a icos --env draft --kind key_value --type team

# 認証情報の設定
orchestrate connections set-credentials -a icos --env draft -e host=https://xxx.cloud -e apikey=xxxx -e instance_id=crn:xxx::
