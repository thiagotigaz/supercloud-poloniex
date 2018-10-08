#!/usr/bin/env python
import argparse
import logging
from time import sleep

import yaml
from poloniex import Poloniex

from supercloud_poloniex.aws_ses import AwsSes
from supercloud_poloniex.margin_closer import MarginCloser

logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s', level=logging.INFO)
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)


def create_argparse():
    parser = argparse.ArgumentParser(description='supercloud poloniex margin closer')
    group = parser.add_argument_group(title='action')
    group.add_argument('-k', '--key', type=str, help='Poloniex Api Key.')
    group.add_argument('-s', '--secret', type=str, help='Poloniex Api Secret.')
    group.add_argument('-awsk', '--aws-key', type=str, help='Aws Key used by SES to send notification emails.')
    group.add_argument('-awss', '--aws-secret', type=str, help='Aws Secret used by SES to send notification emails.')
    group.add_argument('-awsr', '--aws-region', type=str, help='Aws Region used by SES to send notification emails.',
                       default='us-east-1')
    group.add_argument('-lf', '--limit-file', type=str, help='Stop Limit configuration file.', default='limit.yml')
    group.add_argument('-mf', '--monitor-file', type=str, help='Pairs to monitor configuration file.',
                       default='monitor.yml')
    return parser.parse_args()


if __name__ == '__main__':
    args = create_argparse()
    logger.info('Main Args: {}'.format(args))

    with open(args.limit_file, 'r') as stream:
        coins_limit = yaml.load(stream)

    with open(args.monitor_file, 'r') as stream:
        coins_monitor = yaml.load(stream)

    polo = Poloniex(key=args.key, secret=args.secret)
    if args.aws_key and args.aws_secret:
        ses = AwsSes(args.aws_key, args.aws_secret, args.aws_region)
        closer = MarginCloser(polo, coins_limit, coins_monitor, ses=ses)
    else:
        closer = MarginCloser(polo, coins_limit, coins_monitor)

    closer.start()
    while closer._running:
        try:
            sleep(1)
        except Exception as ex:
            print(ex)
            closer.stop()
            break
