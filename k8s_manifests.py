def get_labels():
    return {
            "app": app_name,
            "author": "PavelK",
            "language": "ruby"
            }


def get_affinity():
    return {
                "podAntiAffinity": {
                    "preferredDuringSchedulingIgnoredDuringExecution": [
                        {
                            "podAffinityTerm": {
                                "labelSelector": {
                                    "matchExpressions": [
                                        {
                                            "key": "app",
                                            "operator": "In",
                                            "values": [
                                                app_name
                                            ]
                                        }
                                    ]
                                },
                                "topologyKey": "kubernetes.io/hostname"
                            },
                            "weight": 100
                        }
                    ]
                }
            }


def get_ports():
    return [
                {
                    "containerPort": 80,
                    "protocol": "TCP"
                }
            ]


def get_probe():
    return {
                "exec": {
                    "command": [
                        "curl",
                        "--http0.9",
                        "http://127.0.0.1/healthcheck"
                    ]
                },
                "failureThreshold": 10,
                "initialDelaySeconds": 15,
                "periodSeconds": 10,
                "successThreshold": 1,
                "timeoutSeconds": 60
            }


def get_resources():
    return {
                "limits": {
                    "cpu": "500m",
                    "ephemeral-storage": "2Gi",
                    "memory": "200Mi"
                },
                "requests": {
                    "cpu": "200m",
                    "ephemeral-storage": "1Gi",
                    "memory": "100Mi"
                }
            }


def get_container(image_name):
    probe = get_probe()
    return {
                "name": app_name,
                "image": image_name,
                "imagePullPolicy": "IfNotPresent",
                "lifecycle": {
                    "preStop": {
                        "exec": {
                            "command": [
                                "/bin/sh",
                                "-c",
                                "echo 10 \u003e /tmp/termination \u0026\u0026 sleep 30"
                            ]
                        }
                    }
                },
                "ports": get_ports(),
                "livenessProbe": probe,
                "readinessProbe": probe,
                "resources": get_resources(),
                "terminationMessagePath": "/dev/termination-log",
                "terminationMessagePolicy": "File"
            }


def get_deploy(image_name):
    labels = get_labels()
    return {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {
                        "labels": labels,
                        "name": app_name,
                        "namespace": "default",
                    },
                    "spec": {
                        "minReadySeconds": 5,
                        "progressDeadlineSeconds": 300,
                        "replicas": 3,
                        "revisionHistoryLimit": 5,
                        "selector": {
                            "matchLabels": {
                                "app": app_name
                            }
                        },
                        "strategy": {
                            "rollingUpdate": {
                                "maxSurge": "100%",
                                "maxUnavailable": 0
                            },
                            "type": "RollingUpdate"
                        },
                        "template": {
                            "metadata": {
                                "labels": labels
                            },
                            "spec": {
                                "affinity": get_affinity(),
                                "containers": [get_container(image_name)],
                                "dnsPolicy": "ClusterFirst",
                                "restartPolicy": "Always",
                                "securityContext": {},
                                "terminationGracePeriodSeconds": 60
                            }
                        }
                    }
                }


def get_service():
    return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "labels": get_labels(),
                "name": app_name,
                "namespace": "default",
            },
            "spec": {
                "ports": [
                    {
                        "port": 8080,
                        "protocol": "TCP",
                        "targetPort": 80
                    }
                ],
                "selector": {
                    "app": app_name
                },
                "sessionAffinity": "None",
                "type": "LoadBalancer"
            }
        }


def get_manifests(application_name, image_name):
    global app_name
    app_name = application_name
    return get_deploy(image_name), get_service()