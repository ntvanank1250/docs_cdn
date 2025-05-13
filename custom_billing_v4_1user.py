# Chạy trong python manage.py shell
import json
import pytz
from cdnapi.models import User
from datetime import datetime, date, timedelta
from cdnapi.app import create_app
from redis import Redis
from kafka import KafkaProducer
from cdnapi.utils.audit_billingv4 import send_telegram_message_billing_v4, get_start_month, push_metric_to_billing_v4
load_dotenv()
app = create_app()

# Đoạn cần Custom
current_time = datetime.now() - timedelta(hours=1) # thời gian cần push data
metric_redis = 121121211212 # đơn bị theo Byte
user = User.query.filter_by(email="email").first() #email user

redis_metric = Redis.from_url(app.config["REDIS_METRIC_URL"])
topic = app.config['KAFKA_TOPIC_BILLING_METRICS']
producer = KafkaProducer(
    bootstrap_servers=app.config["KAFKA_BILLING_SERVER"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
    security_protocol=app.config["KAFKA_BILLING_SECURITY_PROTOCOL"],
    sasl_mechanism=app.config["KAFKA_BILLING_SASL_MECHANISM"],
    sasl_plain_username=app.config["KAFKA_BILLING_USERNAME"],
    sasl_plain_password=app.config["KAFKA_BILLING_PASSWORD"]
)
rdbs = Redis.from_url(app.config['REDIS_BILLING_URL'])
local_timezone = pytz.timezone("Asia/Ho_Chi_Minh")
current_time_with_tz = local_timezone.localize(current_time)
current_time_utc = current_time_with_tz.astimezone(pytz.utc)
current_month = current_time.strftime("%m.%Y")
log_path = "/var/log/cdn-api/billing_info_hour_log/{}_{}_{}.log".format(current_time.strftime('%Y'),current_time.strftime('%m'),current_time.strftime('%d'))
if user:
    tenant_id = user.tenant_id
    metric_gb = metric_redis / (1024**3)
    if user.status == "TRIAL":
        push_metric_to_billing_v4(
        tenant_id=tenant_id,
        user=user,
        metric_redis=metric_gb,
        metric_push = metric_gb,
        current_time_utc=current_time_utc,
        current_time=current_time,
        producer=producer,
        topic=topic,
        log_path=log_path,
    )
    elif user.status == "ACTIVE":
        metric_push = 0 
        key_billing = "{}|{}|billing_v4_2th".format(user.email, current_month)
        value_key_billing = float(rdbs.get(key_billing) or 0)

        total = value_key_billing + metric_gb
        if value_key_billing == 0: 
            if total < 200:
                metric_push = 200
            elif total >= 200:
                metric_push = total
        else: 
            if value_key_billing < 200 and total >= 200:
                metric_push = total - 200
            elif value_key_billing >= 200:
                metric_push = metric_gb
        if push_metric_to_billing_v4(
            tenant_id=tenant_id,
            user=user,
            metric_redis=metric_gb,
            metric_push = metric_push,
            total = total,
            current_time_utc=current_time_utc,
            current_time=current_time,
            producer=producer,
            topic=topic,
            log_path=log_path
        ):
            rdbs.set(key_billing, total) #comment nếu không cần cộng thêm data này vào redis
else:
    print("không tìm thấy user")
