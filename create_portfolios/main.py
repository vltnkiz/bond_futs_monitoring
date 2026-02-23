from create_portfolios.core.usecases.futures_basket_download import download_futures_basket
from create_portfolios.core.usecases.definitions_update import update_definitions


def main():
    latest_file = download_futures_basket(save_dir="data/eurex")
    update_definitions(
        csv_file=latest_file,
        bond_json_file="data/portfolios/bond_definition.json",
        future_json_file="data/portfolios/future_definition.json"
    )

if __name__ == "__main__":
    main()
