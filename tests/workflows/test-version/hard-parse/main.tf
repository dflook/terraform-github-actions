terraform {

}

terraform {
  required_version  =  "1.10.4"
}

locals {
  cloud_run_services = [
    {
      service_name = "service-1",
      output_topics = [
        {
          name    = "topic-1",
          version = "v1"
        }
      ]
    }
  ]
}


module "pubsub" {
  for_each = {
    for service in local.cloud_run_services : service.service_name => service
  }
  source = "./module"
  topics = [
    for entity in each.value.output_topics : {
      topic_name        = entity.version != "" ? format("Topic-%s-%s", entity.name, entity.version) : format("Topic-%s", entity.name)
      subscription_name = entity.version != "" ? format("Sub-%s-%s", entity.name, entity.version) : format("Sub-%s", entity.name)
    }
  ]
}


variable "not" {}

variable "should-be-sensitive" {
  sensitive=true
}

variable "not-again" {
  sensitive =          false
}

variable also_sensitive {
  sensitive =  "true"
}

terraform {
  backend "s3" {}
}
