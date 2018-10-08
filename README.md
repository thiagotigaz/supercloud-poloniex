# SuperCloud Poloniex - Margin-Closer and Monitoring
The purpose of this python app is to be able to close margin positions based on upper and lower percentage limits.

It also supports monitoring of pairs and sending emails when a new 24High/24Low is reached or when a margin position is closed.

For sending email it is using Amazon SES and requires an API key with permission to send emails.

## Usage
To configure the app we use two files, one is called ``limit.yml`` which should have configuration for the margin positions and the other is called `monitor.yml`, which should contain a list of coin pairs to be monitored.

Sample Usage:
```
python main.py -k YOUR_POLONIEX_KEY -s YOUR_POLONIEX_SECRET -awsk YOUR_AWS_KEY -awss YOUR_AWS_SECRET
```

Available Options:
```
usage: main.py [-h] [-k KEY] [-s SECRET] [-awsk AWS_KEY] [-awss AWS_SECRET]
               [-awsr AWS_REGION] [-lf LIMIT_FILE] [-mf MONITOR_FILE]

supercloud poloniex margin closer

optional arguments:
  -h, --help            show this help message and exit

action:
  -k KEY, --key KEY     Poloniex Api Key.
  -s SECRET, --secret SECRET
                        Poloniex Api Secret.
  -awsk AWS_KEY, --aws-key AWS_KEY
                        Aws Key used by SES to send notification emails.
  -awss AWS_SECRET, --aws-secret AWS_SECRET
                        Aws Secret used by SES to send notification emails.
  -awsr AWS_REGION, --aws-region AWS_REGION
                        Aws Region used by SES to send notification emails.
  -lf LIMIT_FILE, --limit-file LIMIT_FILE
                        Stop Limit configuration file.
  -mf MONITOR_FILE, --monitor-file MONITOR_FILE
                        Pairs to monitor configuration file.
```

If you want to specify different `limit.yml` or `monitor.yml` files, you can do so using `-lf` for limit or `-mf` for monitor and pass the path of the file.

The AWS email notifications are optional, if no key/secret is passed email won't be sent but margin position will still be closed according to `limit.yml` file.

## Docker Usage
```
docker build -t supercloud-poloniex .
docker run -ti supercloud-poloniex -k YOUR_POLONIEX_KEY -s YOUR_POLONIEX_SECRET -awsk YOUR_AWS_KEY -awss YOUR_AWS_SECRET
```
To mount your own limit and monitor files use following command on the project root directory.
```
docker run -ti -v $(pwd):/app supercloud-poloniex -k YOUR_POLONIEX_KEY -s YOUR_POLONIEX_SECRET -awsk YOUR_AWS_KEY -awss YOUR_AWS_SECRET
```


## Contributions
Contributions are welcome, either refactoring or adding new features, tests, documentation, etc. Just contact me to create a pull request. 

I know this tool is not perfect, I'm not really a full-stack python developer, but I do like to use it for DevOps stuff and tools like this. This script was created in a weekend after I woke up and realized I've lost a bunch of money because of Poloniex's lack of stop order on margin trade. I really hope this can help others to prevent financial loss.

## TODO
* Add documentation to all methods
* Extract monitoring a another module
* Use WsTicker and refactor Monitor and MarginCloser to use data from it
* Add tests
* Add python setup for package distribution
