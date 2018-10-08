import logging
from multiprocessing.dummy import Process
from time import sleep

from supercloud_poloniex.formatter import PartialFormatter

logger = logging.getLogger(__name__)
fmt = PartialFormatter()

UP = 'up'
DOWN = 'down'
LAST = 'last'
BASE_PRICE = 'basePrice'
HIGH_24 = 'high24hr'
LOW_24 = 'low24hr'


class MarginCloser(object):

    def __init__(self, api, coins_limit=None, coins_monitor=None, delay=1, ses=None):
        self.api = api
        self.delay = delay
        self.coins_limit = coins_limit
        self.coins_monitor = coins_monitor
        self.ses = ses
        self.tickers_history = {}

    def start(self):
        """ Start the thread """
        self._process = Process(target=self.run)
        self._process.daemon = True
        self._running = True
        self._process.start()

    def stop(self):
        """ Stop the thread """
        self._running = False
        try:
            self._process.join()
        except Exception as ex:
            logger.exception(ex)

    def filter_empty_positions(self, positions):
        not_tracked = {k: v for k, v in positions.items() if float(v['amount']) != 0 and k not in self.coins_limit}
        if not_tracked:
            logger.warning('You have open margin positions without stop limit set: {}'.format(not_tracked))
        return {k: v for k, v in positions.items() if float(v['amount']) != 0 and k in self.coins_limit}

    def filter_tickers(self, tickers, pairs):
        return {k: v for k, v in tickers.items() if k in pairs}

    def close_position(self, pair):
        logger.info('Closing position for pair {}'.format(pair))
        self.api.closeMarginPosition(pair)

    def run(self):
        """ Main loop, closes open positions if last price is higher or lower than margin base price multiplied by
        up or down configured percentage """
        while self._running:
            try:
                tickers = self.api.returnTicker()
                self.check_margin_positions(tickers)
                self.monitor_prices(tickers)
            except Exception as ex:
                logger.exception(ex)

            finally:
                # sleep with one eye open...
                for i in range(int(self.delay)):
                    if not self._running:
                        break
                    sleep(1)

    def check_margin_positions(self, tickers):
        if self.coins_limit is not None:
            tickers = self.filter_tickers(tickers, self.coins_limit)
            positions = self.filter_empty_positions(self.api.getMarginPosition())
            for k, v in positions.items():
                ticker, pair_limit = tickers[k], self.coins_limit[k]
                up = pair_limit[UP] * float(v[BASE_PRICE]) if UP in pair_limit else None
                down = pair_limit[DOWN] * float(v[BASE_PRICE]) if DOWN in pair_limit else None
                last = float(ticker[LAST])
                pos_status = fmt.format('{0} base: {1:.8f} last: {2:.8f} up: {3:.8f} down: {4:.8f}', k,
                                        float(v[BASE_PRICE]), last, up, down)
                logger.info(pos_status)
                if (up is not None and last >= up) or (down is not None and last <= down):
                    self.close_position(k)
                    self.send_email('SOLD: {}'.format(pos_status))

    def monitor_prices(self, tickers):
        if self.coins_monitor is not None:
            email_content = ''
            tickers = self.filter_tickers(tickers, self.coins_monitor)
            if not self.tickers_history:
                self.tickers_history = tickers
            for k, v in tickers.items():
                previous_ticker = self.tickers_history[k]
                if v[HIGH_24] > previous_ticker[HIGH_24] or v[LOW_24] < previous_ticker[LOW_24]:
                    email_content += '{} New {} -> High: {} Low: {} Last: {}\r\n'.format(
                        k, 'High' if v[HIGH_24] > previous_ticker[HIGH_24] else 'Low', v[HIGH_24], v[LOW_24], v[LAST])
            if email_content:
                self.send_email(email_content)
            self.tickers_history = tickers

    def send_email(self, content):
        if self.ses is not None:
            logger.info('Sending email. Content: {}'.format(content))
            self.ses.send_email(content)
