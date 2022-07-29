from src.actions.cmd_prompt_actions import CommandPromptActions
from src.actions.csv_file_operator import CsvFileOperator


def main():
    actions = CommandPromptActions.create("header.txt")
    actions.start()
    actions.set_csv()
    datatypes = actions.set_datatypes()

    file_as_string = actions.get_filepath()

    op = CsvFileOperator.bootstrap(file_as_string, datatypes)
    actions.print(op.file_status())

    csv = op.gen_new_csv("SUCCESS.csv")
    op.delete_old_csv(csv)

    op.write_csv(csv)
    actions.print(op.file_status())

    op.to_cash_flow_csv("Namn", csv)
    actions.print(op.file_status())

    actions.stop()


if __name__ == '__main__':
    main()
