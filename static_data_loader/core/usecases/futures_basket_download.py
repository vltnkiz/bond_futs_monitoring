from static_data_loader.adapters.eurex_futures_basket_downloader import EurexFuturesBasketDownloader

def download_futures_basket(save_dir) -> str:
    downloader = EurexFuturesBasketDownloader()
    return downloader.download(save_dir=save_dir)
