"""Module to count CHAI."""

import os
from typing import TypedDict

from dotenv import load_dotenv
import pandas as pd
from web3 import Web3
from ens import ENS
from pyairtable.api.table import Table


class AirtableSettings(TypedDict):
    """This class defines the airtable settings."""
    apikey: str
    chaiform: str
    projform: str


class Record(TypedDict):
    """This class defines an airtable record."""
    id: str
    createdTime: str
    fields: dict[str, object]


def ens(endpoint) -> ENS:
    """ This function retrieves ENS endpiont. """

    w3_provider: Web3.HTTPProvider = Web3.HTTPProvider(endpoint)
    assert w3_provider.isConnected()
    ens_endpoint: ENS = ENS(provider=w3_provider)

    return ens_endpoint


def get_wallet_addresses(airtable_settings: AirtableSettings) -> dict[str, str]:
    """ This function maps discord ID to wallet addresses. """
    # retrieve relevant info from CHAI form
    table_chai: list[Record] = Table(
        airtable_settings["apikey"], airtable_settings["chaiform"], 'Table 1'
    ).all(fields=['Discord Handle', 'Wallet Address'])  # type: ignore

    # map authors to wallet addresses
    wallet_addresses: dict[str, str] = {}
    for record in table_chai:
        wallet_addresses.update(
            {record['fields']["Discord Handle"]: record['fields']
                ["Wallet Address"]}  # type: ignore
        )

    return wallet_addresses


def get_p2p_data(path) -> pd.DataFrame:
    """ This function creates a dataframe  discord data df. """

    # retrieve raw discord log
    csv_posts: list[str] = sorted(os.listdir(path))
    df_posts: pd.DataFrame = pd.concat(
        map(pd.read_csv, [path+"/"+i for i in csv_posts]), ignore_index=True
    )

    # prune columns & remove NaN
    necessary_columns: list[str] = ["Author", "Date", "Reactions"]
    df_column_pruned: pd.DataFrame = df_posts[necessary_columns].dropna()

    # filter by p2p
    df_has_p2p: pd.DataFrame = df_column_pruned[df_column_pruned['Reactions'].str.contains(
        "p2p")].reset_index(drop=True)  # type: ignore

    # format datetime
    df_has_p2p['Date'] = df_has_p2p['Date'].map(pd.to_datetime)

    # sort by date
    df_has_p2p_bydate: pd.DataFrame = df_has_p2p.sort_values(
        by=['Date']).reset_index(drop=True)

    return df_has_p2p_bydate


def count_chai_p2p(df_chatlog, chai_per_p2p, airtable_settings, ens_endpoint) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ This function counts p2p posts by author. """

    # initialize {discord_id: p2p_amount}
    chai_p2p: dict[str, int] = dict.fromkeys(
        df_chatlog.copy().drop_duplicates(subset="Author").reset_index(drop=True).Author,
        0
    )
    # obtain a dictionary {discord_id: p2p_amount}
    for i in range(len(df_chatlog)):
        chai_p2p[df_chatlog.Author[i]] += chai_per_p2p * \
            int(df_chatlog.Reactions[i].split("p2p ")[-1][1:2])

    wallet_addresses: dict[str, str] = get_wallet_addresses(airtable_settings)

    # map author's wallet addresses to CHAI amount
    chai_distribution_p2p: list[list] = []
    verbose_list: list[list] = []
    for recipient, chai_amount in chai_p2p.items():
        # resolve ENS to address if necessary
        try:
            if wallet_addresses[recipient][:2] == "0x":
                pass
            elif wallet_addresses[recipient][-4:] == ".eth":
                try:
                    wallet_addresses[recipient] = str(
                        ens_endpoint.address(wallet_addresses[recipient]))
                except:
                    print(
                        f"ENS name {wallet_addresses[recipient]} doesn't resolve to an address."
                    )
            else:
                print(
                    f"{wallet_addresses[recipient]} is an invalid wallet address.")

            chai_distribution_p2p.append(
                [wallet_addresses[recipient], chai_amount])

            # write verbose output including discord Id
            verbose_list.append(
                [recipient, chai_amount])

        except:
            print(f"could not find {recipient}'s wallet address.")

    csv_p2p: pd.DataFrame = pd.DataFrame(
        chai_distribution_p2p, columns=["receiver", "amount"])
    csv_p2p["token_type"], csv_p2p["token_address"] = [
        "erc20", "0x4491D1c47bBdE6746F878400090ba6935A91Dab6"]
    csv_p2p = csv_p2p[["token_type", "token_address", "receiver", "amount"]]

    verbose_output: pd.DataFrame = pd.DataFrame(
        verbose_list, columns=["receiver", "amount"])

    return csv_p2p, verbose_output


def count_chai_projects(chai_per_project, airtable_settings, time_start, time_end, ens_endpoint) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ This function counts project completions by each user."""

    # retrieve relevant info from Project Completion form
    table_projform: Table = Table(
        airtable_settings["apikey"], airtable_settings["projform"], 'Table 1'
    )
    projcomp_list: list[Record] = table_projform.all(
        fields=['Discord Handle', 'Wallet address', 'CHAI_done', 'Created'])  # type: ignore

    wallet_addresses: dict[str, str] = get_wallet_addresses(airtable_settings)

    # create list of wallet addresses and CHAI amount for each project completion
    chai_distribution_proj: list[list] = []
    verbose_dict: dict[str, int] = {}
    for record in projcomp_list:

        try:

            completed_date: pd.Timestamp = pd.to_datetime(
                record['fields']['Created']).tz_localize(None)  # type: ignore

            if record['fields']['CHAI_done'] != "no":
                pass
            elif not (
                    pd.to_datetime(time_start) <= completed_date
                    and completed_date <= pd.to_datetime(time_end)):
                pass
            else:
                # resolve ENS to address if necessary
                if record['fields']['Wallet address'][:2] == "0x":  # type: ignore
                    pass
                elif record['fields']['Wallet address'][-4:] == ".eth":  # type: ignore
                    try:
                        record['fields']['Wallet address'] = str(
                            ens_endpoint.address(record['fields']['Wallet address']))
                    except:
                        print(
                            f"ENS name {record['fields']['Wallet address']} doesn't resolve to an address."
                        )
                else:
                    print(
                        f"{record['fields']['Wallet address']} is an invalid wallet address.")

                # add record to list
                chai_distribution_proj.append(
                    [record['fields']['Wallet address'], chai_per_project]
                )

                # write verbose output including discord Id
                if record['fields']['Discord Handle'] in verbose_dict.keys():
                    verbose_dict[record['fields']['Discord Handle']
                                 ] += chai_per_project  # type: ignore
                else:
                    verbose_dict[record['fields']['Discord Handle']
                                 ] = chai_per_project  # type: ignore

                # update CHAI_done field
                table_projform.update(record['id'], {'CHAI_done': 'yes'})
        except:
            pass

    csv_proj: pd.DataFrame = pd.DataFrame(
        chai_distribution_proj, columns=["receiver", "amount"])
    csv_proj["token_type"], csv_proj["token_address"] = [
        "erc20", "0x4491D1c47bBdE6746F878400090ba6935A91Dab6"]
    csv_proj = csv_proj[["token_type", "token_address", "receiver", "amount"]]

    verbose_output: pd.DataFrame = pd.DataFrame(
        verbose_dict.items(), columns=["receiver", "amount"])

    return csv_proj, verbose_output


def write_csv_for_airdrop(df_output: pd.DataFrame,  filename: str) -> bool:
    """ write to csv formatted for gnosis safe CSV airdrop """
    try:
        os.makedirs("./output_csv", exist_ok=True)
        df_output[["token_type", "token_address", "receiver", "amount"]].to_csv(
            f"./output_csv/{filename}.csv", header=True, index=False)
        print(f"csv for {filename} done.")
        return True
    except:
        print(f"no CHAI for {filename}.")
        return False


def write_csv_for_logging(df_output: pd.DataFrame,  folder: str, category: str) -> bool:
    """ write to csv formatted for human reading tying discord ID to CHAI received """
    months: dict[str, str] = {
        "01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June",
        "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"
    }

    try:
        os.makedirs("./verbose_record", exist_ok=True)
        df_output[["receiver", "amount"]].to_csv(
            f"./verbose_record/LOG--{months[folder[5:7]]}_{category}.csv", header=True, index=False)
        return True
    except:
        return False


def main(folder: str, time_start: str, time_end: str):
    """ Main function. """
    print("now starting CHAIcounter! \n")

    ### load settings ###
    alchemy_endpoint: str = str(os.getenv("ALCHEMY_ENDPOINT"))
    airtable_settings: AirtableSettings = {
        "apikey": str(os.getenv("AIRTABLE_API")),
        "chaiform": str(os.getenv("AIRTABLE_BASE_CHAI")),
        "projform": str(os.getenv("AIRTABLE_BASE_PROJECT"))
    }
    chai_per_p2p: int = int(str(os.getenv("CHAI_PER_P2P")))
    chai_per_project: int = int(str(os.getenv("CHAI_PER_PROJECT")))

    ### connect to RPC endpoint (for resolving ENS addresses) ###
    print("connecting RPC endpoint...")
    ens_connection: ENS = ens(alchemy_endpoint)

    ### scan discord log ###
    print(f"reading discord chat data from `./discord_log/{folder}` ...")
    data_path: str = os.path.join(os.getcwd(), f"./discord_log/{folder}")
    p2p_df: pd.DataFrame = get_p2p_data(data_path)

    ### count CHAI for P2P ###
    print("counting CHAI to distribute (p2p)...")
    output_csv_p2p, output_verbose_p2p = count_chai_p2p(
        p2p_df, chai_per_p2p, airtable_settings, ens_connection)

    print("writing token distribution (p2p) output to csv...")
    write_csv_for_airdrop(output_csv_p2p, f"{folder}_p2p")
    write_csv_for_logging(output_verbose_p2p, folder, "p2p")

    ### count CHAI for project completion ###
    print("counting CHAI to distribute (project completion)...")
    output_csv_projects, output_verbose_projects = count_chai_projects(
        chai_per_project, airtable_settings, time_start, time_end, ens_connection)

    # write to csv for token multisend
    write_csv_for_airdrop(output_csv_projects, f"{folder}_projectcompletion")
    write_csv_for_logging(output_verbose_projects, folder, "projectcompletion")

    print(
        f"\n all done! check file at `./output_csv/{folder}_***.csv`")


load_dotenv(os.path.join(os.getcwd(), '.env'))
if pd.to_datetime(str(os.getenv("folderName"))) >= pd.to_datetime('today'):
    main(str(os.getenv("folderName")), str(
        os.getenv("Af")), str(pd.to_datetime('today')))
else:
    main(str(os.getenv("folderName")), str(
        os.getenv("Af")), str(os.getenv("Bf")))
