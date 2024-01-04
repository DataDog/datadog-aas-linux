This readme outlines how to set up Datadog tracing with your Azure App Service Linux application. Making the following changes in the Azure portal will allow the tracer to initialize when your application is started.

_Note: Currently Java, NODE, .NET, PHP and Python are supported._

### Application Settings
- `DD_API_KEY` is your Datadog API key
- `DD_SITE` is the Datadog site [parameter](https://docs.datadoghq.com/getting_started/site/#access-the-datadog-site) (defaults to datadoghq.com)
- `DD_SERVICE` is the service name used for this program. Defaults to the name field value in package.json.
- `DD_START_APP` is the command used to start your application. For example, `node ./bin/www` (Unnecessary for Tomcat applications)

![](https://p-qkfgo2.t2.n0.cdn.getcloudapp.com/items/v1uPLYrR/e0f4e84d-b9bf-4f90-838c-f1771cc9d95d.jpg?v=54a84161784fcf4f1df606fbf7195a65)

### General Settings
##### Node, .NET, PHP or Python
Add the following to the startup command box

      curl -s https://raw.githubusercontent.com/DataDog/datadog-aas-linux/v1.7.0/datadog_wrapper | bash

![](https://p-qkfgo2.t2.n0.cdn.getcloudapp.com/items/8LuqpR7e/6a9bf63d-5169-49d0-a68a-20e6e3009d47.jpg?v=7704a16bc91a6a57caf8befd84204415)

##### Java

Download the `datadog_wrapper` file from the releases and upload it to your application with the [Azure CLI command](https://learn.microsoft.com/en-us/azure/app-service/deploy-zip?tabs=cli#deploy-a-startup-script):

      az webapp deploy --resource-group <group-name> --name <app-name> --src-path <path-to-datadog-wrapper> --type=startup

### Viewing traces

1. Azure will restart the application when new Application Settings are saved. However, a restart may be required for the startup command to be recognized by App Services if it is added and saved at a different time.

2. After the AAS application restarts, the traces can be viewed by searching for the service name (DD_SERVICE) in the [APM Service page](https://docs.datadoghq.com/tracing/services/service_page/) of your Datadog app.

### Custom Metrics

To enable custom metrics for your application with DogStatsD, add  `DD_CUSTOM_METRICS_ENABLED` and set it as `true` in your Application Settings.

To configure your application to submit metrics, follow the appropriate steps for your runtime.

- [Java](https://docs.datadoghq.com/developers/dogstatsd/?tab=hostagent&code-lang=java)
- [Node](https://github.com/brightcove/hot-shots)
- [.NET](https://docs.datadoghq.com/developers/dogstatsd/?tab=hostagent&code-lang=dotnet#code)
- [PHP](https://docs.datadoghq.com/developers/dogstatsd/?tab=hostagent&code-lang=php)
- [Python](https://docs.datadoghq.com/developers/dogstatsd/?tab=hostagent&code-lang=python)