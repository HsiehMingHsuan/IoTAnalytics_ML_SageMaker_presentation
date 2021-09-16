import json
import time
import os
import numpy as np

import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.model as model

if __name__ == '__main__':
    ipc_client = awsiot.greengrasscoreipc.connect()

    specs1 = [1, 0.1, 1000]
    specs2 = [10, 1, 2000]
    cov = [[1, 0, 0], [0, 1, 0], [0, 0, 2]]
    s = True
    while True:
        if s:
            gen = np.random.multivariate_normal(specs1, cov, 1)
            s = False
        else: 
            gen = np.random.multivariate_normal(specs2, cov, 1)
            s = True
        gen = np.squeeze(gen)
        gen.tolist()
        telemetry_data = {
            "timestamp": int(round(time.time() * 1000)),
            "battery_state_of_charge": 42.5,
            "location": {
                "longitude": 48.15743,
                "latitude": 11.57549,
            },
            "instantaneous_discharge": gen[0],
            "fluid_velocity": gen[1],
            "accumulated_heat": gen[2],
        }

        op = ipc_client.new_publish_to_iot_core()
        op.activate(model.PublishToIoTCoreRequest(
            topic_name="my/iot/{}/telemetry".format(os.getenv("AWS_IOT_THING_NAME")),
            qos=model.QOS.AT_LEAST_ONCE,
            payload=json.dumps(telemetry_data).encode(),
        ))
        try:
            result = op.get_response().result(timeout=5.0)
            print("successfully published message:", result)
        except Exception as e:
            print("failed to publish message:", e)

        time.sleep(5)