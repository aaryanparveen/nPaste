import argparse
import requests
import sys


BASE_URL = "http://127.0.0.1:5000"

def create_paste(content, title=None, language=None, tags=None, private=False):
    url = f"{BASE_URL}/api/paste"
    payload = {
        "content": content,
        "title": title,
        "language": language,
        "tags": tags,
        "private": private
    }
    
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        print(f"Success! Paste created at: {data['url']}")
        print(f"Raw URL: {data['raw_url']}")
    except Exception as e:
        print(f"Error creating paste: {e}")

def search_pastes(query=None, tag=None):
    url = f"{BASE_URL}/api/search"
    params = {}
    if query:
        params['q'] = query
    if tag:
        params['tag'] = tag
        
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        results = r.json()
        
        if not results:
            print("No pastes found.")
            return

        print(f"Found {len(results)} pastes:")
        print("=" * 60)
        for paste in results:
            tags = f"[{', '.join(paste['tags'])}]" if paste['tags'] else ""
            print(f"TITLE: {paste['title']} ({paste['language']}) {tags}")
            print(f"URL:   {paste['url']}")
            print("-" * 60)
            print(paste.get('content', ''))
            print("=" * 60)
            print()
            
    except Exception as e:
        print(f"Error searching pastes: {e}")

def main():
    parser = argparse.ArgumentParser(description="nPaste CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')


    create_parser = subparsers.add_parser('create', help='Create a new paste (default)')
    create_parser.add_argument('input_file', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="File to paste (or stdin)")
    create_parser.add_argument('--title', '-t', help="Paste Title")
    create_parser.add_argument('--lang', '-l', help="Language (e.g. python, text)")
    create_parser.add_argument('--tags', help="Comma separated tags")
    create_parser.add_argument('--private', '-p', action='store_true', help="Make private")


    search_parser = subparsers.add_parser('search', help='Search for pastes')
    search_parser.add_argument('query', nargs='?', help="Search query")
    search_parser.add_argument('--tag', help="Filter by tag")
    if len(sys.argv) > 1 and sys.argv[1] not in ['create', 'search', '-h', '--help']:
        sys.argv.insert(1, 'create')

    args = parser.parse_args()
    
    if args.command == 'search':
        if not args.query and not args.tag:
            print("Please provide a query or tag to search.")
            return
        search_pastes(args.query, args.tag)
        
    elif args.command == 'create' or args.command is None:
        if args.input_file.isatty():
            print("Usage: echo 'hello' | python npaste_cli.py [create]")
            print("   OR: python npaste_cli.py search 'query'")
            return

        content = args.input_file.read()
        if not content:
            print("Empty content.")
            return

        create_paste(content, args.title, args.lang, args.tags, args.private)

if __name__ == "__main__":
    main()
