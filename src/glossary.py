import niad_glossary
import utils


def main():
    config = utils.get_config()
    niad_glossary.extract_glossary_url_list(config)


if __name__ == "__main__":
    main()
