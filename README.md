# Multi-User Stock Trade Management System

**A Data Structures and Algorithms course project using a custom Hash Table and a linked-list FIFO Queue.** The current Python CLI loads stock positions and historical prices from CSV and lets you inspect the accepted data in memory.

When two accounts hold the same stock, their positions can have different entry prices and exit rules. Each lot has its own position ID. The ticker index groups those lots so that a future replay can find the positions affected by each price update.

## Run the demo

Use Python 3.10 or later. The demo uses the Python standard library.

```text
python -B code/main.py
```

Run the command from the repository root. The menu accepts paths to your own files. Press **Enter** at a path prompt to use the bundled sample.

| Menu option | What it does |
| --- | --- |
| **1. Load portfolio from CSV** | Loads accounts and positions, checks IDs and ownership, and builds indexes by account ID, position ID and ticker. |
| **2. Load market prices from CSV** | Validates price events and puts them in the Queue in file order. |
| **3. View current data** | Lists accounts, shows one account's positions, or displays the loaded price file's metadata. |
| **0. Exit** | Ends the program. |

For a quick demo, choose **1** and press Enter twice. Choose **2** and press Enter. Then choose **3** to inspect the **3 accounts, 6 positions and 25 price events across 5 tickers**. Try account `A01` to see its three positions or `A03` to see an account with no positions. `A01` and `A02` both hold FPT in separate lots.

## Input files

| File | Columns |
| --- | --- |
| `accounts.csv` | `account_id,account_name` |
| `positions.csv` | `position_id,account_id,ticker,quantity,entry_price,stop_loss_pct,take_profit_pct,trailing_stop_pct` |
| `prices.csv` | `timestamp,ticker,price` |

Each position references an existing account. An empty rule cell disables that rule. Prices are in VND per share, and price timestamps use ISO 8601 with the `+07:00` offset. The loader rejects backward timestamps and duplicate timestamp/ticker pairs. Events for different tickers at the same time retain their file order. If a load fails, the last successfully loaded data is still available.

## Read the code

| File or folder | Responsibility |
| --- | --- |
| [code/main.py](code/main.py) | Runs the menu, calls the loaders and opens the views. |
| [code/csv_reader.py](code/csv_reader.py) | Reads CSV rows and checks the header and row width. |
| [code/loaders.py](code/loaders.py) | Validates the field values and builds the portfolio indexes or price Queue. |
| [code/views.py](code/views.py) | Formats the loaded data for the terminal. |
| [code/dsa/](code/dsa/) | Implements the reusable Hash Table and linked Queue. |
| [code/models/](code/models/) | Defines the data fields for accounts, positions, price events and price-source metadata. |
| [code/samples/](code/samples/) | Holds the three input CSVs used by the demo. |

The Hash Table uses separate chaining and starts with 16 buckets. It doubles and rehashes when the load factor exceeds 0.75. For short keys and well-distributed buckets, exact-key lookup takes expected `O(1)`. The Queue keeps head and tail pointers so enqueue and dequeue each take `O(1)`.

## Project milestones

P1–P3 cover loading and inspecting data. The next milestones are **P4** historical replay, exit rule evaluation and simulated fills, then **P5** summary and results.
