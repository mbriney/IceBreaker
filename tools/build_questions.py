"""Builds questions.js for Icebreaker.

Run:  python3 tools/build_questions.py
Each category mixes hand-written questions with templates whose fill-in
lists were written to fit that template, so every line reads naturally.
"""
import itertools, json, random, re, pathlib

rng = random.Random(1858)

def T(template, items):
    return [template.format(x=i) for i in items]

def pairs(template, items, cap=None):
    out = [template.format(a=a, b=b) for a, b in itertools.combinations(items, 2)]
    if cap and len(out) > cap:
        out = rng.sample(out, cap)
    return out

def triples(template, items, cap):
    out = [template.format(a=a, b=b, c=c) for a, b, c in itertools.combinations(items, 3)]
    rng.shuffle(out)
    return out[:cap]

def lines(block):
    return [l.strip() for l in block.strip().splitlines() if l.strip()]

C = {}  # id -> list

# ---------------------------------------------------------------- Just for Fun
hot_take = ["pineapple on pizza", "socks with sandals", "cereal as a dinner", "the Oxford comma", "reclining your airplane seat",
    "putting ketchup on eggs", "replying-all", "voice memos instead of texts", "decorating for Christmas in October",
    "talking during movies", "eating the crust", "dipping fries in a milkshake", "wearing pajamas in public",
    "keeping the TV on for background noise", "leaving dishes to soak", "using speakerphone in public", "tipping at a counter",
    "the five-second rule", "folding pizza", "cold pizza for breakfast", "hot dogs being sandwiches", "candy corn",
    "gender-reveal parties", "open-concept homes", "sleeping with socks on", "the middle armrest", "spoilers after a week",
    "drinking milk with dinner", "putting milk in before cereal", "toilet paper over vs. under", "naming your car",
    "clapping when the plane lands", "dogs in restaurants", "white walls", "sparkling water", "the snooze button",
    "matching family outfits", "people who stand on escalators", "pumpkin spice everything", "raisins in cookies"]
skills = ["parallel parking", "karaoke", "assembling furniture", "keeping plants alive", "remembering names", "packing a suitcase",
    "giving directions", "telling jokes", "wrapping presents", "cooking without a recipe", "board games", "trivia nights",
    "keeping secrets", "being on time", "dancing at weddings", "napping", "haggling", "folding fitted sheets",
    "taking selfies", "staying calm in traffic", "picking a restaurant", "making small talk", "whistling", "doing impressions",
    "giving gifts", "reading maps", "cleaning up after a party", "keeping a straight face", "guessing someone's age",
    "spotting a celebrity", "skipping stones", "throwing a frisbee", "flipping pancakes", "carrying all the groceries in one trip",
    "finding a good parking spot", "making a playlist", "winning arguments", "getting a baby to laugh", "eating spicy food",
    "keeping New Year's resolutions"]
places = ["at a wedding", "on an airplane", "in a grocery store", "at a theme park", "on a family road trip", "at a sporting event",
    "in an elevator", "at a concert", "at school", "on a first day at a new job", "at a holiday dinner", "at a restaurant",
    "at the DMV", "on public transit", "at a hotel", "on a camping trip", "at a birthday party", "in a drive-thru",
    "at the beach", "at the gym", "at a museum", "at a yard sale", "in a hospital waiting room", "on a cruise",
    "at a gas station", "at a high school reunion", "at a zoo", "during a power outage", "at a car wash", "at a pet store"]
ideal3 = ["Saturday", "birthday", "vacation", "breakfast", "road trip", "night in", "night out", "snow day", "Sunday morning",
    "summer afternoon", "holiday", "house", "pizza", "dinner party", "weekend away", "workday", "playlist", "outfit",
    "neighborhood", "birthday cake", "date night", "concert", "game night", "picnic", "morning routine", "cup of coffee",
    "rainy day", "bookstore", "backyard", "retirement"]
over_under = ["holiday", "snack", "fruit", "board game", "movie genre", "fast-food chain", "vegetable", "candy", "breakfast cereal",
    "dessert", "city", "sport", "season", "chore", "hobby", "car feature", "kitchen gadget", "app", "condiment",
    "ice cream flavor", "pizza topping", "Halloween costume", "drink", "type of weather", "day of the week",
    "school subject", "cartoon", "dog breed", "song to sing at karaoke", "tourist attraction", "smell", "font",
    "color", "piece of furniture", "decade for fashion", "type of shoe", "sandwich", "soup", "bread", "time of day"]
theme_song = ["Monday mornings", "your commute", "your entrance into a party", "doing chores", "your workout", "your daily coffee run",
    "a bad hair day", "payday", "your first cup of coffee", "your weekend", "when you win an argument", "a road trip",
    "cleaning the kitchen", "walking into a meeting", "the last day of vacation", "getting good news", "your morning alarm",
    "getting out of bed", "stuck in traffic", "finishing a big project", "your birthday", "a snow day", "grocery shopping",
    "cooking dinner", "your bedtime routine"]
name_it = ["a pet goldfish", "a boat", "a food truck", "your future band", "your autobiography", "a racehorse", "a new crayon color",
    "a hurricane", "a signature cocktail", "a new holiday", "your home Wi-Fi network", "a fancy candle scent", "a racecar",
    "a new ice cream flavor", "a podcast about your life", "a robot vacuum", "a pet rock", "your alter ego", "a new dance move",
    "a houseplant", "a talk show", "a sandwich named after you", "a superhero version of you", "a hot sauce", "a cereal",
    "a llama", "a bakery", "a board game about your family", "a perfume", "a sailboat"]
excuse = ["being late", "skipping the gym", "leaving a party early", "not answering a call", "missing a deadline",
    "eating dessert first", "not doing the dishes", "staying in on a Friday", "forgetting a birthday", "not finishing a book",
    "cancelling plans", "being on your phone at dinner", "buying something you didn't need", "taking a nap",
    "ordering takeout again", "not replying to a text", "wearing the same outfit twice", "skipping a meeting",
    "not making your bed", "eating the last slice", "hitting snooze", "missing a workout class", "not calling back",
    "watching one more episode", "not mowing the lawn"]
best_way = ["spend a rainy day", "cure hiccups", "eat an Oreo", "fall asleep fast", "wake up in the morning", "spend $20",
    "make a boring meeting fun", "kill 15 minutes", "cheer up a friend", "survive a long flight", "beat the heat",
    "warm up on a cold day", "celebrate a small win", "start a weekend", "eat a slice of pizza", "spend a snow day",
    "pass time in a waiting room", "end a long day", "make new friends as an adult", "break the ice with a stranger",
    "spend a lazy Sunday", "use a free afternoon", "get over a cold", "start a conversation on an elevator",
    "make someone laugh", "pick a movie", "settle an argument", "load a dishwasher", "organize a closet", "split a dessert"]
emoji_desc = ["your Monday", "your morning routine", "your cooking skills", "your last vacation", "your love life",
    "your workweek", "your family group chat", "your bedroom right now", "your music taste", "your driving",
    "your sense of humor", "your fashion sense", "your dance moves", "your weekend plans", "your phone screen time",
    "your fridge", "your inbox", "your coffee habit", "your hometown", "your last haircut", "your sleep schedule",
    "your current mood", "your workout routine", "your relationship with mornings", "your inner child"]
C["fun"] = (
    T("What's your hot take on {x}?", hot_take)
    + T("On a scale of 1 to 10, how good are you at {x}?", skills)
    + T("What's your secret technique for {x}?", skills)
    + T("What's the funniest thing that's ever happened to you {x}?", places)
    + T("What's the weirdest thing you've ever seen {x}?", places)
    + T("Describe your ideal {x} in three words.", ideal3)
    + T("What's the most overrated {x}?", over_under)
    + T("What's the most underrated {x}?", over_under)
    + T("What's the perfect theme song for {x}?", theme_song)
    + T("What would you name {x}?", name_it)
    + T("What's your go-to excuse for {x}?", excuse)
    + T("What's the best way to {x}?", best_way)
    + T("Which emoji best describes {x}?", emoji_desc)
    + lines("""
What's a hill you're willing to die on?
What's the most useless talent you have?
What's the strangest thing you've ever eaten on a dare?
What's a word you always mispronounce?
What's the most ridiculous thing you've ever bought?
What's your most irrational fear?
What would your wrestling entrance music be?
What would your pro-wrestler name be?
What's the silliest argument you've ever had?
What's a smell that instantly makes you happy?
What celebrity do people say you look like?
What's the worst haircut you've ever had?
What's your go-to karaoke song?
What's your signature dance move?
What's the most embarrassing song on your playlist?
What's something you're weirdly competitive about?
What's the most random fact you know?
If you were a ghost, who or what would you haunt?
What would your last meal be if it had to come from a gas station?
What's the worst gift you've ever received?
What's the most spontaneous thing you've ever done?
Which fictional world would you least want to live in?
What's a conspiracy theory you secretly enjoy?
What's your go-to sound effect?
What's the strangest thing in your junk drawer?
What's the longest you've gone without sleep, and why?
What's the best prank you've ever pulled or witnessed?
What's your most-used phrase?
What's your favorite useless invention?
What's the dumbest way you've ever hurt yourself?
"""))

# ------------------------------------------------------------- Would You Rather
powers = ["fly", "be invisible", "read minds", "teleport", "breathe underwater", "talk to animals", "time travel",
    "freeze time", "speak every language", "have super strength", "never need sleep", "shape-shift", "control the weather",
    "heal any injury", "see the future", "have perfect memory", "run at super speed", "walk through walls",
    "become any age at will", "talk to plants", "control fire", "move objects with your mind", "never feel cold",
    "instantly master any skill by watching it once"]
homes = ["a treehouse", "a houseboat", "a castle", "a lighthouse", "a log cabin", "a penthouse", "a tiny house", "a space station",
    "an igloo", "a farmhouse", "a submarine", "a yurt", "a converted train car", "a desert dome", "a Parisian apartment"]
only_eat = ["pizza", "tacos", "sushi", "burgers", "pasta", "fried chicken", "pancakes", "salad", "ramen", "barbecue",
    "sandwiches", "curry", "breakfast food", "soup"]
pets = ["a dragon", "a talking cat", "a miniature elephant", "a penguin", "a small dinosaur", "a unicorn", "a fox", "an owl",
    "a sloth", "a giant tortoise", "an otter", "a griffin", "a teacup pig", "a monkey"]
give_up = ["the internet", "coffee", "music", "dessert", "air travel", "your phone", "cheese", "TV", "books", "chocolate",
    "social media", "hot showers", "takeout", "air conditioning", "your car", "bread"]
eras = ["ancient Egypt", "the Wild West", "the Roaring Twenties", "the year 3000", "the age of dinosaurs", "Renaissance Florence",
    "1960s London", "the first Moon landing", "the ancient Olympics", "the 1980s", "Victorian England", "medieval Japan",
    "ancient Rome", "Woodstock", "the signing of the Declaration of Independence"]
master = ["the piano", "a second language", "surfing", "cooking", "painting", "coding", "the guitar", "ballroom dancing",
    "public speaking", "chess", "magic tricks", "woodworking", "photography", "rock climbing", "singing"]
jobs = ["astronaut", "chef", "park ranger", "rock star", "professional athlete", "movie director", "marine biologist",
    "detective", "architect", "zookeeper", "pilot", "novelist", "late-night talk show host", "ice cream taster", "video game designer"]
C["wyr"] = (
    pairs("Would you rather be able to {a} or {b}?", powers)
    + pairs("Would you rather live in {a} or {b}?", homes)
    + pairs("Would you rather eat only {a} or only {b} for a year?", only_eat)
    + pairs("Would you rather have {a} or {b} as a pet?", pets)
    + pairs("Would you rather give up {a} or {b} forever?", give_up)
    + pairs("Would you rather spend a day in {a} or {b}?", eras)
    + pairs("Would you rather instantly master {a} or {b}?", master)
    + pairs("Would you rather work as a(n) {a} or a(n) {b} for a year?", jobs)
    + lines("""
Would you rather always be 10 minutes late or always be 20 minutes early?
Would you rather know how you'll die or when you'll die?
Would you rather have a rewind button or a pause button for your life?
Would you rather be famous now and forgotten later, or unknown now and famous after you die?
Would you rather never be able to lie or never be able to tell when someone is lying?
Would you rather have unlimited free travel or unlimited free food?
Would you rather fight one horse-sized duck or a hundred duck-sized horses?
Would you rather sing everything you say or dance everywhere you go?
Would you rather have a personal chef or a personal driver?
Would you rather lose your sense of taste or your sense of smell?
Would you rather be the funniest person in the room or the smartest?
Would you rather live without music or without movies?
Would you rather be able to speak to animals or speak every human language?
Would you rather have more time or more money?
Would you rather always have to whisper or always have to shout?
Would you rather explore space or the deep ocean?
Would you rather be a master of every instrument or every sport?
Would you rather have your dream job or your dream house?
Would you rather relive your best day or skip your worst?
Would you rather have a photographic memory or be able to forget anything you want?
Would you rather be stuck on a broken elevator or a broken Ferris wheel?
Would you rather be the best player on a losing team or the worst player on a winning team?
Would you rather never have to clean again or never have to cook again?
Would you rather have a third arm or a third eye?
Would you rather know every language or be able to play every instrument?
Would you rather live where it's always summer or always winter?
Would you rather have a rooftop pool or a home movie theater?
Would you rather be an amazing dancer or an amazing singer?
Would you rather win the lottery or live twice as long?
Would you rather have free Wi-Fi everywhere or free coffee everywhere?
Would you rather read the book or watch the movie first?
Would you rather have a robot butler or a self-driving car?
Would you rather always know the right thing to say or always know the right thing to do?
Would you rather be able to pause live TV in real life or rewind conversations?
Would you rather go back to age 10 with what you know now, or fast-forward 10 years?
Would you rather be a kid in your parents' generation or your kids' generation?
Would you rather have a tail or wings that don't work?
Would you rather have everything you eat be too salty or not salty enough?
Would you rather hike a mountain or kayak a river?
Would you rather spend a weekend with your favorite author or your favorite musician?
"""))

# ------------------------------------------------------------------ Quick Picks
tot_groups = [
    ["coffee", "tea", "hot chocolate", "lemonade", "iced tea", "sparkling water", "a milkshake", "orange juice", "a smoothie", "root beer"],
    ["sunrise", "sunset", "high noon", "midnight", "golden hour", "the middle of the night"],
    ["spring", "summer", "fall", "winter"],
    ["pancakes", "waffles", "French toast", "a breakfast burrito", "bacon and eggs", "a bagel", "oatmeal", "a donut", "cereal", "biscuits and gravy"],
    ["beach vacation", "mountain cabin", "big-city trip", "cruise", "road trip", "camping trip", "theme park", "staycation", "ski trip", "safari"],
    ["dogs", "cats", "birds", "fish", "horses", "rabbits", "reptiles", "hamsters"],
    ["books", "movies", "TV shows", "podcasts", "video games", "board games", "puzzles", "audiobooks"],
    ["texting", "calling", "video chat", "voice memos", "email", "handwritten letters"],
    ["chocolate", "vanilla", "strawberry", "mint chip", "cookie dough", "rocky road", "butter pecan", "salted caramel"],
    ["sneakers", "boots", "sandals", "flip-flops", "loafers", "barefoot"],
    ["rock", "country", "hip-hop", "pop", "jazz", "classical", "R&B", "folk", "'80s hits", "musical theater"],
    ["early bird", "night owl", "afternoon napper", "all-day energizer"],
    ["sweet", "salty", "spicy", "sour", "savory"],
    ["city life", "small town", "suburbs", "the countryside", "off the grid"],
    ["pizza", "burgers", "tacos", "sushi", "pasta", "Thai", "Chinese takeout", "barbecue", "Indian", "Mediterranean"],
    ["hoodie", "flannel", "denim jacket", "suit", "sweatpants", "sundress", "leather jacket", "cozy sweater"],
    ["Marvel", "DC", "Star Wars", "Star Trek", "Harry Potter", "The Lord of the Rings"],
    ["roller coasters", "water slides", "Ferris wheels", "haunted houses", "carousels", "bumper cars"],
    ["fireplace", "hot tub", "porch swing", "hammock", "bay window", "backyard fire pit"],
    ["paper books", "e-reader", "audiobook"],
    ["shower in the morning", "shower at night"],
    ["window seat", "aisle seat"],
    ["plan everything", "wing it"],
    ["mountains", "ocean", "desert", "forest", "lake", "prairie"],
    ["popcorn", "nachos", "candy", "pretzels", "hot dog", "ice cream"],
    ["chips", "cookies", "fruit", "cheese and crackers", "popcorn", "trail mix", "veggies and dip", "candy"],
    ["thunderstorms", "snowfall", "sunny days", "fog", "light rain", "crisp fall wind"],
    ["Halloween", "Thanksgiving", "Christmas", "New Year's Eve", "Fourth of July", "your birthday", "Valentine's Day"],
    ["football", "baseball", "basketball", "hockey", "soccer", "tennis", "golf", "the Olympics"],
    ["comedy", "horror", "romance", "action", "documentary", "sci-fi", "mystery", "animated"],
]
rank_groups = [
    ["pizza", "tacos", "sushi", "burgers", "pasta", "fried chicken", "ramen", "barbecue", "curry", "dumplings", "grilled cheese", "nachos", "pho", "lasagna", "fajitas"],
    ["Halloween", "Thanksgiving", "Christmas", "New Year's Eve", "Fourth of July", "Valentine's Day", "your birthday", "Easter", "Labor Day", "St. Patrick's Day", "Mother's Day", "Groundhog Day"],
    ["dogs", "cats", "horses", "dolphins", "elephants", "penguins", "owls", "otters", "foxes", "pandas", "bears", "giraffes", "sloths", "koalas"],
    ["beach", "mountains", "big city", "desert", "lake cabin", "forest", "island", "small town", "wine country", "ski resort", "national park", "cruise ship"],
    ["chocolate", "vanilla", "strawberry", "mint chip", "cookie dough", "rocky road", "pistachio", "butter pecan", "salted caramel", "coffee", "cookies and cream", "rainbow sherbet"],
    ["flying", "invisibility", "teleporting", "mind reading", "time travel", "super strength", "talking to animals", "super speed", "healing", "shape-shifting", "breathing underwater", "freezing time"],
    ["spring", "summer", "fall", "winter", "the holiday season", "the first warm week of the year", "the first snow"],
    ["comedy", "horror", "romance", "action", "documentary", "sci-fi", "mystery", "animated", "musical", "western", "fantasy", "thriller"],
    ["the beach", "a theme park", "a museum", "a concert", "a ballgame", "a zoo", "a farmers market", "a bookstore", "a spa", "a hiking trail", "a county fair", "an escape room"],
    ["coffee", "tea", "soda", "lemonade", "hot chocolate", "sparkling water", "smoothies", "milkshakes", "iced tea", "orange juice"],
]
C["picks"] = []
for g in tot_groups:
    C["picks"] += pairs("{a} or {b}?", g)
for g in rank_groups:
    C["picks"] += triples("Rank these, best to worst: {a}, {b}, {c}.", g, 45)
for g in rank_groups[:6]:
    C["picks"] += triples("Keep one, ditch one, swap one: {a}, {b}, {c}.", g, 20)
C["picks"] = [q[0].upper() + q[1:] for q in C["picks"]]

# ---------------------------------------------------------------- Food & Drink
best_had = ["pizza", "taco", "burger", "steak", "slice of cake", "cup of coffee", "sandwich", "bowl of soup", "breakfast",
    "barbecue", "pie", "bowl of pasta", "plate of fries", "ice cream cone", "cookie", "bowl of ramen", "hot dog",
    "fried chicken", "plate of sushi", "pancakes", "glass of lemonade", "doughnut", "salad", "burrito", "grilled cheese",
    "cinnamon roll", "seafood dinner", "mac and cheese", "milkshake", "homemade meal"]
take_your = ["coffee", "steak", "eggs", "tea", "burger", "hot dog", "toast", "popcorn", "pizza", "baked potato", "nachos",
    "salad", "oatmeal", "fries", "pancakes"]
go_to_order = ["coffee shop", "pizza place", "Chinese takeout spot", "diner", "sandwich shop", "taco truck", "burger joint",
    "ice cream shop", "sushi restaurant", "bakery", "barbecue joint", "Mexican restaurant", "Italian restaurant",
    "fast-food drive-thru", "ballpark concession stand", "movie theater", "state fair", "breakfast spot", "Thai restaurant",
    "smoothie bar", "deli", "bar and grill", "food court", "steakhouse", "gas station"]
cook_for = ["a first date", "your in-laws", "a celebrity chef", "a picky six-year-old", "a holiday crowd of 20", "a sick friend",
    "your boss", "a backyard cookout", "a potluck", "a midnight snack", "a lazy Sunday brunch", "your childhood hero",
    "someone who's never tried your culture's food", "a camping trip", "a tailgate", "a bake sale", "a new neighbor",
    "a dinner party", "a game-night crowd", "a romantic anniversary"]
a_food_you = ["loved as a kid but can't stand now", "hated as a kid but love now", "could eat every day", "will never try again",
    "think is overrated", "think everyone should try", "crave when you're sad", "crave when you're celebrating",
    "always order when you see it on a menu", "can make better than any restaurant", "associate with a specific person",
    "associate with a specific place", "secretly love even though it's 'junk'", "eat in a weird way", "could never give up",
    "only eat on holidays", "pretend to like", "have strong opinions about", "would serve at your wedding",
    "would bring to a deserted island", "eat when no one's watching", "think is perfect for breakfast", "wish were healthy",
    "want to learn to make", "always overeat"]
ultimate = ["sandwich", "pizza topping combo", "comfort food", "pizza", "breakfast", "dessert", "burger build", "taco",
    "salad", "ice cream sundae", "hot dog build", "nacho platter", "milkshake", "snack board", "road-trip snack",
    "movie-night snack", "birthday dinner", "holiday side dish", "Sunday dinner", "brunch spread", "smoothie", "soup",
    "pasta dish", "late-night snack", "cookie", "cake", "pie", "cereal combo", "grilled-cheese upgrade", "breakfast sandwich"]
fav_food = ["spice", "cheese", "pasta shape", "kind of bread", "fruit", "vegetable", "condiment", "hot sauce", "potato style",
    "candy bar", "cookie", "pie", "soup", "cereal", "chip flavor", "type of cuisine", "kitchen smell", "holiday dish",
    "breakfast food", "kind of pickle", "sandwich bread", "nut", "berry", "herb", "kind of salad", "dipping sauce",
    "type of tea", "coffee drink", "soda", "flavor of jam", "type of cake", "kind of taco", "pizza crust", "ice cream topping",
    "family recipe", "street food", "seafood", "kind of noodle", "melon", "apple variety"]
best_eat = ["after a long day", "on a road trip", "at a ballgame", "at midnight", "when you're sick", "on a cold day", "at the beach",
    "at a movie", "while watching football", "on vacation", "after a workout", "at a picnic", "on a rainy day", "at a campfire",
    "on a first date", "at a wedding", "at a sleepover", "in the car", "when you're stressed", "on your birthday"]
tried = ["escargot", "frog legs", "alligator", "oysters", "sea urchin", "durian", "haggis", "kimchi", "natto", "blood sausage",
    "bone marrow", "octopus", "rattlesnake", "bison", "jackfruit", "lutefisk", "fried pickles", "chicken feet", "caviar", "liver and onions",
    "deep-fried butter", "crickets", "goat curry", "ceviche", "a ghost pepper", "beef tongue", "squid ink pasta", "venison", "rabbit", "tripe"]
open_a = ["food truck", "diner", "bakery", "coffee shop", "pizza place", "breakfast café", "ice cream shop", "barbecue joint",
    "sandwich shop", "fancy restaurant", "late-night snack bar", "cereal bar", "dessert bar", "tea room", "taco stand"]
food_wyr = ["pizza", "tacos", "sushi", "burgers", "pasta", "fried chicken", "ramen", "barbecue", "curry", "steak", "salad", "pancakes", "dumplings", "gumbo"]
C["food"] = (
    T("What's the best {x} you've ever had?", best_had)
    + T("How do you take your {x}?", take_your)
    + T("What's your go-to order at a {x}?", go_to_order)
    + T("What would you cook for {x}?", cook_for)
    + T("What's a food you {x}?", a_food_you)
    + T("What's your ultimate {x}?", ultimate)
    + T("What's your favorite {x}?", fav_food)
    + T("What's the best thing to eat {x}?", best_eat)
    + T("Have you ever tried {x}? Would you again?", tried)
    + T("If you opened a {x}, what would be on the menu?", open_a)
    + triples("Rank these, best to worst: {a}, {b}, {c}.", food_wyr, 80)
    + lines("""
What's the most memorable meal you've ever had?
What's your signature dish?
What was a staple meal in your house growing up?
What's the strangest food combination you love?
What's your favorite restaurant of all time?
What's a food you'd travel across the world to eat?
What's your favorite holiday food tradition?
What's your biggest kitchen disaster?
Who taught you to cook?
What's one recipe you'd want passed down in your family?
What's the spiciest thing you've ever eaten?
What's your go-to snack when you're up late?
What's your coffee order, exactly?
Do you have a favorite grocery store? Why?
What dish reminds you most of home?
What's the fanciest meal you've ever had?
What's your favorite meal to eat outdoors?
What food do you always have in your fridge?
What's one food you've never tried but want to?
What's the most adventurous thing you've ever ordered?
Are you a cook-at-home person or an eat-out person?
What's your favorite thing to bake?
What's the best food city you've ever visited?
What's a dish you've tried to perfect?
What's your favorite cookbook or food show?
What would your food truck be called?
What do you always order for dessert?
What's your favorite drink to make at home?
Cake or pie? Defend your answer.
What's your favorite thing to grill?
"""))

# ------------------------------------------------------------- Travel & Places
month_in = ["Paris", "Tokyo", "Rome", "New Zealand", "Iceland", "Bali", "Peru", "Morocco", "Ireland", "Greece", "Thailand",
    "Kenya", "Argentina", "Norway", "Vietnam", "Scotland", "Portugal", "Costa Rica", "Egypt", "India", "Australia",
    "Alaska", "Hawaii", "Mexico City", "Barcelona", "London", "Istanbul", "Cape Town", "Seoul", "Vancouver", "Prague",
    "Amsterdam", "Havana", "Buenos Aires", "the Swiss Alps", "Tuscany", "Kyoto", "Patagonia", "the Galápagos", "Montana",
    "New Orleans", "Nashville", "Maine", "the Scottish Highlands", "the Amalfi Coast", "Croatia", "Jordan", "Tasmania",
    "the Canadian Rockies", "Sicily"]
teleport = ["the top of the Eiffel Tower", "the Great Wall of China", "Machu Picchu", "the Grand Canyon", "the pyramids of Giza",
    "the northern lights", "Times Square on New Year's Eve", "the Great Barrier Reef", "Yellowstone", "the Taj Mahal",
    "Antarctica", "the Colosseum", "Niagara Falls", "Mount Everest base camp", "Victoria Falls", "Santorini at sunset",
    "a Tokyo sushi counter", "the Serengeti", "Petra", "Angkor Wat", "Stonehenge", "a Venice canal", "the Sistine Chapel",
    "a Hawaiian volcano", "the Sahara at night", "Central Park in fall", "a Swiss chalet", "a Scottish castle",
    "the Amazon rainforest", "a Paris café", "Mount Rushmore", "the Dead Sea", "a Norwegian fjord", "Bora Bora",
    "a Kentucky Derby", "Rio during Carnival", "a London pub", "the Golden Gate Bridge", "the Badlands at sunrise", "the Moon"]
vibe_for = ["a honeymoon", "a family reunion", "a solo trip", "a big birthday", "a long weekend", "a girls' or guys' trip",
    "a work retreat", "a holiday break", "a spring break", "an anniversary", "a graduation trip", "a cheap getaway",
    "a once-in-a-lifetime trip", "a winter escape", "a summer vacation"]
story = ["airport", "hotel", "road trip", "lost luggage", "camping", "getting lost", "missed flight", "rental car",
    "travel buddy", "language barrier", "best tour guide", "food poisoning", "weather disaster", "upgrade",
    "street food", "souvenir", "border crossing", "hostel", "cruise", "train"]
must_pack = ["a beach trip", "a camping trip", "a long flight", "a road trip", "a ski trip", "a business trip", "a trip to Europe",
    "a weekend at a cabin", "a theme park day", "a cruise", "a music festival", "a trip with kids", "a backpacking trip",
    "a wedding weekend", "a tropical vacation", "a trip somewhere freezing", "a hiking day", "a weekend at the lake",
    "a girls' or guys' weekend", "a staycation"]
dest_pairs = ["Paris", "Tokyo", "Rome", "Iceland", "Bali", "New York City", "London", "Hawaii", "the Alps", "Australia",
    "Egypt", "Peru", "Greece", "Thailand", "Ireland", "Alaska", "Costa Rica", "Morocco", "Norway", "the Caribbean"]
C["travel"] = (
    T("If you could spend a month in {x}, what would you do first?", month_in)
    + T("If you could teleport to {x} for one hour, what would you do?", teleport)
    + T("Beach, mountains, or city for {x}? Why?", vibe_for)
    + T("What's your best {x} story?", story)
    + T("What's your must-pack item for {x}?", must_pack)
    + pairs("Which would you rather visit: {a} or {b}?", dest_pairs)
    + lines("""
What's the best trip you've ever taken?
What's at the top of your travel bucket list?
What's the most beautiful place you've ever seen?
Where's somewhere you've been that you'd never go back to?
What's the farthest you've ever traveled from home?
Are you a planner or a wing-it traveler?
What's your favorite souvenir you've brought home?
What's a place that completely surprised you?
What's your dream road trip route?
What's the best meal you've had while traveling?
Window seat or aisle seat, and why?
What's the most underrated place you've visited?
What's your favorite thing to do in a new city?
Would you rather travel solo or with a group?
What city could you see yourself living in someday?
What's the most adventurous thing you've done on a trip?
What's the best hotel or place you've ever stayed?
What's a tourist trap that was actually worth it?
What's your favorite national park or outdoor place?
If you could live abroad for a year, where would you go?
What's your favorite airport and why?
What's a place from a movie you'd love to visit?
What's your favorite way to travel: plane, train, car, or boat?
What's a trip you took as a kid that you still remember?
What's the best thing about your hometown?
What would you show a visitor in your town if they had one day?
What's the most spontaneous trip you've ever taken?
What's your best travel hack?
What's a place you've visited that felt like home?
Where would you go if you had a free plane ticket today?
"""))

# --------------------------------------------------------------------- Childhood
fav_kid = ["cartoon", "toy", "cereal", "board game", "book", "candy", "lunchbox", "video game", "TV show", "movie", "band",
    "subject in school", "recess game", "sport", "holiday", "stuffed animal", "Halloween costume", "fast-food meal",
    "snack", "song", "after-school activity", "superhero", "dinner your family made", "birthday party", "summer activity",
    "field trip", "teacher", "outfit", "hiding spot", "Saturday morning ritual", "ice cream truck treat", "school lunch",
    "magazine", "card game", "bike", "backyard game", "pretend game", "trading card", "theme park", "camp activity",
    "rainy-day activity", "family vacation spot", "pet", "drink", "sticker", "joke", "fort you built", "nickname",
    "holiday tradition", "neighborhood hangout"]
memory_smile = ["birthday", "holiday", "summer vacation", "school field trip", "snow day", "family road trip", "sleepover",
    "first day of school", "grandparent", "camp", "backyard", "sibling", "neighborhood", "sports", "library", "pet",
    "Christmas morning", "Halloween", "Fourth of July", "kitchen"]
fav_who = ["teacher", "cartoon character", "athlete", "musician", "superhero", "author", "TV host", "coach", "movie star",
    "babysitter", "neighbor", "cousin", "fictional villain", "video game character", "aunt or uncle"]
family_always = ["on Sunday nights", "on road trips", "at Thanksgiving", "on birthdays", "at the dinner table", "in the summer",
    "when someone was sick", "on the first day of school", "on holidays", "on snow days", "on Friday nights",
    "on the Fourth of July", "on vacation", "on Saturday mornings", "when it rained"]
from_childhood = ["you wish kids still had", "that would confuse kids today", "you still have", "you'd bring back",
    "that scared you", "you begged your parents for", "you got in trouble for", "you were secretly proud of",
    "you were obsessed with", "you thought was magic", "you still can't explain", "you were sure was true",
    "you collected", "you wanted to grow up to be", "that you'd never let your own kids do", "that shaped who you are",
    "that still makes you laugh", "you miss the most", "you were afraid to admit", "you wish you'd paid more attention to"]
kid_toys = ["LEGO", "Barbie", "Hot Wheels", "a Game Boy", "a Tamagotchi", "a Nintendo", "a skateboard", "a bike", "Beanie Babies",
    "Pokémon cards", "a trampoline", "a treehouse", "a slip 'n slide", "a walkie-talkie set", "an Easy-Bake Oven", "Nerf guns"]
C["kid"] = (
    T("What was your favorite {x} as a kid?", fav_kid)
    + T("What's a childhood {x} memory that still makes you smile?", memory_smile)
    + T("Who was your favorite {x} growing up?", fav_who)
    + T("What did your family always do {x}?", family_always)
    + T("What's one thing from your childhood {x}?", from_childhood)
    + pairs("What was cooler as a kid: {a} or {b}?", kid_toys)
    + lines("""
What did you want to be when you grew up?
What was your childhood nickname?
What was your first pet's name?
What's the earliest memory you have?
Who was your best friend in elementary school?
What's the worst trouble you got into as a kid?
What was your bedroom like growing up?
What was your first concert?
What was the first movie you saw in a theater?
What was your first job?
What's a rule your parents had that you didn't understand until later?
What was your favorite thing about summer break?
What did you spend your allowance on?
Were you a rule follower or a rule breaker as a kid?
What's a smell that takes you straight back to childhood?
What was your go-to after-school snack?
What was your favorite thing to do at your grandparents' house?
What's a song that instantly takes you back?
What did you think adults did all day?
What was the best gift you got as a kid?
What's the most childish thing you still do?
What was your favorite game to play outside?
What was your favorite place to hide?
What did you believe as a kid that turned out to be false?
Did you have an imaginary friend?
What was your favorite day of the year as a kid?
What was the hardest thing about being a kid?
What's a lesson from childhood that stuck with you?
What did you want to name your future kids when you were little?
What's a trend from your childhood you'd like to forget?
"""))

# ---------------------------------------------------------------- Work & Career
best_ever = ["boss", "job", "team", "mentor", "piece of career advice", "interview question you've been asked", "coworker",
    "work trip", "office party", "workspace", "project", "day at work", "compliment from a colleague", "class you've taken",
    "training you've had"]
how_do = ["stay focused", "recharge after a long week", "handle a tough email", "prep for a big meeting", "deal with a bad day",
    "start your workday", "end your workday", "beat the afternoon slump", "say no to extra work", "keep track of your to-dos",
    "handle a mistake you made", "celebrate a win", "learn something new for your job", "make a hard decision",
    "give tough feedback", "get unstuck on a problem", "manage your inbox", "keep meetings short", "get to know new coworkers",
    "handle nerves before a presentation", "balance work and home", "stay motivated on a long project", "take a real break",
    "ask for help", "keep your desk organized"]
job_in = ["a pirate crew", "a medieval castle", "a space station", "a circus", "a heist movie", "the Old West",
    "a zombie apocalypse", "a rock band", "a pro sports team", "a royal court", "a Broadway show", "a submarine crew",
    "Santa's workshop", "a superhero team", "a 1920s newspaper", "a cooking competition", "a wizarding school",
    "a moon colony", "a treasure hunt", "a theme park"]
take_on = ["open offices", "meetings before 9 a.m.", "reply-all", "cameras on for video calls", "four-day workweeks",
    "standing desks", "office snacks", "working from home", "team-building exercises", "casual Fridays", "business cards",
    "LinkedIn", "inbox zero", "dress codes", "office birthday celebrations", "after-hours emails", "Slack or Teams messages",
    "working from a coffee shop", "office music", "unlimited vacation", "networking events", "ties", "whiteboards",
    "lunch meetings", "the office thermostat", "group projects", "annual reviews", "PowerPoint", "conference swag",
    "hybrid schedules"]
do_job = ["air traffic controller", "kindergarten teacher", "surgeon", "chef", "news anchor", "airline pilot", "judge",
    "firefighter", "zookeeper", "wedding planner", "librarian", "museum curator", "game show host", "farmer", "nurse",
    "stand-up comedian", "park ranger", "personal trainer", "car salesperson", "auctioneer", "lighthouse keeper",
    "fashion designer", "orchestra conductor", "rodeo clown", "barista", "real estate agent", "lifeguard", "mail carrier",
    "dentist", "tour guide", "sports referee", "mayor", "flight attendant", "talk show host", "detective", "hairstylist",
    "TV weather forecaster", "pastry chef", "ship captain", "veterinarian"]
perks = ["a nap pod", "free lunch every day", "a four-day week", "unlimited vacation", "a dog-friendly office", "an on-site gym",
    "a corner office", "a fully paid sabbatical", "a company car", "a free coffee bar", "a shorter commute", "a bigger title",
    "flexible hours", "a remote-work stipend", "free concert tickets", "a yearly team trip"]
C["work"] = (
    T("What's the best {x} you've ever had?", best_ever)
    + T("How do you {x}?", how_do)
    + T("What would your job be in {x}?", job_in)
    + T("What's your take on {x}?", take_on)
    + T("Could you be a(n) {x} for a day? What would go wrong?", do_job)
    + pairs("Which perk would you take: {a} or {b}?", perks)
    + lines("""
What was your very first job?
What's the weirdest job you've ever had?
What's your dream job if money didn't matter?
What's the best career advice you've ever received?
What did you want to be when you were 10?
What's a skill you've picked up at work that helps you in life?
What's one thing you'd change about your job?
What's the hardest work lesson you've learned?
What's a project you're really proud of?
Who's someone you've learned a lot from at work?
What's your most productive time of day?
What's on your desk right now?
What's your favorite work tool or app?
What does a perfect workday look like for you?
What's your favorite thing about your job?
What's the funniest thing that's happened to you at work?
What was your first paycheck spent on?
What's the most valuable thing a manager ever did for you?
If you could swap jobs with anyone here for a day, who would it be?
What's a job you could never do?
What's a part of your job people would be surprised by?
What's the best team you've ever been on, and why?
What's your favorite way to celebrate a win at work?
Coffee meeting or walking meeting?
What's something you're trying to get better at professionally?
What's your work superpower?
What's the best meeting you've ever been in?
What's a work habit you're trying to break?
What job would you be terrible at?
What does success look like to you this year?
"""))

# --------------------------------------------------------------------- What If
dinner_any = ["historical figure", "fictional character", "athlete", "musician", "scientist", "president", "author", "chef",
    "explorer", "inventor", "artist", "comedian", "movie star", "ancestor", "philosopher", "astronaut"]
learn_any = ["language", "instrument", "sport", "dance", "craft", "cuisine", "martial art", "science", "magic trick", "trade"]
if_you_were = ["kitchen appliance", "dog breed", "font", "color", "season", "kind of weather", "board game", "cereal",
    "ice cream flavor", "car", "tree", "piece of furniture", "city", "superhero", "sound", "holiday", "spice", "emoji",
    "shoe", "sandwich", "candle scent", "fruit", "bird", "song", "painting", "dessert", "musical instrument", "time of day",
    "cocktail", "national park", "planet", "app on a phone", "sport", "type of tree", "flower", "breakfast food",
    "movie genre", "smell", "gemstone", "school subject"]
woke_as = ["a cat", "the President", "a famous chef", "a golden retriever", "a pop star", "a toddler", "an astronaut on the ISS",
    "a billionaire", "a pro athlete", "your boss", "your best friend", "a bird", "a 90-year-old", "a movie villain",
    "a medieval king or queen", "a famous painter", "a dolphin", "a ghost", "a giant", "a Hollywood director",
    "a lighthouse keeper", "the opposite gender", "your pet", "a superhero", "a time traveler from 1850"]
live_inside = ["a movie", "a video game", "a painting", "a song", "a book", "a TV show", "a board game", "a fairy tale",
    "a cartoon", "a snow globe"]
add_one = ["holiday to the calendar", "subject to school", "room to your house", "day to the week", "rule to every workplace",
    "amendment to the Constitution", "Olympic event", "flavor to every ice cream shop", "feature to your phone",
    "button to your car", "law everyone must follow", "food to every menu", "animal to the zoo", "chore robots must do",
    "class every kid takes", "national park", "color to the rainbow", "season to the year", "sense to the human body",
    "hour to the day"]
do_with = ["a million dollars", "a free day with no obligations", "a private jet for a week", "a time machine",
    "an extra hour every day", "a robot assistant", "a year off", "an empty warehouse", "a private island",
    "a blank check for one dinner", "a personal chef for a month", "a city's budget for a day", "the ability to pause time for an hour",
    "a do-over on one decision", "a magic lamp with three wishes", "a ticket to anywhere", "your own TV channel",
    "a billboard in Times Square", "a stadium full of people listening", "a team of 50 volunteers", "a full year of free travel",
    "a mansion for a weekend", "a million followers", "a famous painting", "a world-record attempt",
    "a superpower for one day", "an invisible cloak", "a castle", "a farm", "a racehorse"]
stranded = ["on a desert island", "in a cabin during a snowstorm", "on a space station", "on a sailboat at sea",
    "in a library overnight", "in a mall overnight", "in an airport for 24 hours", "on a mountaintop", "in a lighthouse",
    "on a train across the country"]
C["whatif"] = (
    T("If you could have dinner with any {x}, who would it be?", dinner_any)
    + T("If you could instantly learn any {x}, which would you pick?", learn_any)
    + T("If you were a {x}, what would you be and why?", if_you_were)
    + T("If you woke up as {x} for a day, what would you do?", woke_as)
    + T("If you had to live inside {x}, which one would you choose?", live_inside)
    + T("If you could add one {x}, what would it be?", add_one)
    + T("What would you do with {x}?", do_with)
    + T("If you were stranded {x}, what three things would you want?", stranded)
    + lines("""
If you could relive one day of your life, which would it be?
If you could ask your future self one question, what would it be?
If you could master any skill overnight, what would it be?
If you could change one thing about the world, what would it be?
If animals could talk, which would be the rudest?
If you could only listen to one album forever, what would it be?
If your life were a movie, who would play you?
If you could time travel once, past or future?
If you could have any view from your window, what would it be?
If you could un-invent one thing, what would it be?
If you could meet one fictional character, who would it be?
If you had to wear one outfit forever, what would it be?
If you could be famous for one thing, what would it be?
If you won an award, what would it be for?
If you could switch lives with someone for a week, who would it be?
If you could bring back one extinct animal, which would it be?
If you could solve one mystery, which would it be?
If you could have a conversation with your 10-year-old self, what would you say?
If you could live in any era, which would you choose?
If you could only eat at one restaurant forever, which one?
If you were a villain, what would your evil plan be?
If you could be any age for a week, what age would you be?
If you were invisible for a day, what would you do?
If you could design your dream house, what's the one must-have room?
If you could make one thing free for everyone, what would it be?
If your pet could talk, what would it say about you?
If you started a band, what instrument would you play?
If you could star in any TV show, which would it be?
If you had a warning label, what would it say?
If you could be the world's best at something, what would it be?
"""))

# --------------------------------------------------------------- Movies, Music & TV
best_all_time = ["movie sequel", "theme park ride based on a movie", "sitcom", "cartoon", "album", "road trip song",
    "movie soundtrack", "Christmas movie", "animated movie", "TV finale", "Halloween movie", "movie villain", "movie hero",
    "movie line", "movie trilogy", "TV intro song", "boy band", "girl group", "love song", "breakup song", "one-hit wonder",
    "Super Bowl halftime show", "music video", "reality show", "game show", "talk show host", "sports movie", "musical",
    "movie remake", "kids' show", "cooking show", "documentary", "comedy special", "superhero movie", "movie car",
    "movie dog", "fictional school", "fictional city", "fictional family", "song to dance to"]
char_as = ["roommate", "boss", "best friend", "lawyer", "teacher", "travel buddy", "personal chef", "coach", "neighbor",
    "bodyguard", "wedding planner", "tour guide", "life coach", "co-pilot", "doctor", "therapist", "sidekick",
    "personal stylist", "babysitter", "team captain"]
song_for = ["a walk-up song", "a first dance", "a road trip kickoff", "a karaoke showstopper", "your morning alarm",
    "a workout", "cleaning the house", "a rainy day", "a summer barbecue", "a sad day", "a graduation", "a victory lap",
    "a slow dance", "falling asleep", "a sing-along in the car", "the end credits of your life", "a holiday party",
    "a first date", "a breakup", "a long drive at night", "a lazy Sunday", "cooking dinner", "a pep talk",
    "Friday afternoon", "a campfire", "a wedding reception", "your entrance at a party", "a moment of calm",
    "a sunrise", "a celebration"]
watch_movie = ["at least once", "on a rainy day", "at Thanksgiving", "on a first date", "with their family", "when they're sad",
    "before they turn 30", "on a plane", "at a sleepover", "around the holidays", "with a big group", "alone",
    "after a breakup", "on a snow day", "before a big trip", "to feel inspired", "to laugh until they cry",
    "to understand you better", "with their kids", "on a summer night"]
C["pop"] = (
    T("What's the best {x} of all time?", best_all_time)
    + T("Which movie character would you want as your {x}?", char_as)
    + T("Which TV character would you want as your {x}?", char_as)
    + T("Which cartoon character would you want as your {x}?", char_as)
    + T("What song would you pick for {x}?", song_for)
    + T("What movie should everyone watch {x}?", watch_movie)
    + lines("""
What movie can you quote word for word?
What's a show you've rewatched more than three times?
What was the last show you binge-watched?
What's a movie that made you cry?
What's the first album you ever bought?
What's the best concert you've ever been to?
What song is stuck in your head right now?
What's your guilty-pleasure TV show?
What's a movie everyone loves that you can't stand?
Who's an artist you'll always defend?
What's a book that should be made into a movie?
What's the scariest movie you've ever seen?
Which movie world would you want to live in?
What's your all-time favorite movie?
Which celebrity would you want to be best friends with?
What's the most overrated movie ever?
What's a song that always gets you on the dance floor?
What TV family is most like yours?
What musician would you love to see live?
What's a movie you've never seen that everyone says you should?
What's your favorite decade for music?
What's a song you know every word to?
What's the best book you've read this year?
What podcast are you into right now?
What's a show you wish hadn't been canceled?
What's your favorite movie snack?
What's the best live performance you've ever seen?
If you could be in any band, which would it be?
What's your go-to comfort movie?
What fictional character are you most like?
"""))

# ------------------------------------------------------------- Hobbies & Skills
tried_act = ["skydiving", "scuba diving", "pottery", "rock climbing", "surfing", "knitting", "archery", "fly fishing",
    "ballroom dancing", "beekeeping", "sailing", "woodworking", "improv comedy", "painting", "bird watching", "gardening",
    "golf", "yoga", "horseback riding", "kayaking", "calligraphy", "baking bread", "photography", "geocaching",
    "stand-up paddleboarding", "skiing", "snowboarding", "fencing", "glassblowing", "pickleball", "running a marathon",
    "hot-air ballooning", "learning an instrument", "camping alone", "foraging", "candle making", "metal detecting",
    "axe throwing", "cross-stitch", "trivia leagues", "bowling leagues", "chess tournaments", "community theater",
    "singing in a choir", "volunteering", "home brewing", "astronomy", "cosplay", "model trains", "genealogy"]
fav_way = ["spend a Saturday", "unwind", "get outside", "be creative", "stay active", "spend a snow day", "spend a summer evening",
    "learn something new", "spend time alone", "spend time with friends", "use your hands", "spend a lazy afternoon",
    "challenge yourself", "relax on vacation", "spend a long weekend", "clear your head", "spend an evening at home",
    "spend a sunny morning", "be social", "spend money on a hobby"]
act_pairs = ["pottery", "rock climbing", "surfing", "painting", "woodworking", "sailing", "golf", "photography", "cooking classes",
    "salsa dancing", "archery", "kayaking", "gardening", "improv", "yoga", "skiing", "fly fishing", "horseback riding",
    "baking", "pickleball", "chess", "guitar", "bird watching", "hiking", "knitting"]
C["hobby"] = (
    T("Have you ever tried {x}? Would you want to?", tried_act)
    + T("What's your favorite way to {x}?", fav_way)
    + pairs("Which would you rather try: {a} or {b}?", act_pairs)
    + lines("""
What hobby would you pick up if you had unlimited time?
What hobby would you pick up if money were no object?
What's a hobby you've abandoned?
What's something you could teach this group in 10 minutes?
What's a skill you're secretly proud of?
What's a skill you wish you had learned as a kid?
What's the most recent thing you taught yourself?
What's your favorite thing to do with your hands?
What's a hobby people would never guess you have?
What do you collect, or what did you used to collect?
What's a skill that you think everyone should have?
What's something you're surprisingly good at?
What's a class you'd love to take?
What hobby do you spend the most money on?
What's an activity that makes you lose track of time?
If you could go pro in any hobby, which would it be?
What's the last thing you made with your own hands?
What's your favorite game to play with a group?
What's an outdoor activity you love?
What's a hobby you'd like to share with someone you love?
What's your favorite thing to do on a day off?
What's a goal you're working toward outside of work?
What's the hardest thing you've ever learned to do?
Who got you into your favorite hobby?
What's a skill you've been meaning to learn for years?
What's your favorite thing to do on a rainy day?
Do you prefer hobbies that are relaxing or challenging?
What's your proudest creation?
What's a tradition you've turned into a hobby?
What's a hobby you think is underrated?
"""))

# --------------------------------------------------------------- All About You
whats_your = ["hidden talent", "love language", "go-to comfort food", "morning routine", "biggest pet peeve", "guilty pleasure",
    "favorite way to spend a day off", "most-used app", "spirit animal", "proudest moment", "biggest fear", "hidden passion",
    "most prized possession", "lucky number", "favorite smell", "favorite word", "favorite quote", "go-to compliment",
    "go-to dance move", "favorite sound", "favorite season", "favorite room in your house", "happy place", "favorite holiday",
    "favorite color", "favorite way to say thank you", "signature scent", "dream car", "favorite time of day", "comfort show",
    "secret skill", "most-worn piece of clothing", "best quality", "worst habit", "favorite family tradition",
    "favorite thing about yourself", "favorite way to celebrate", "most useful life hack", "favorite thing to talk about",
    "go-to coffee or tea order"]
describe_you = ["your best friend", "your mom", "your dog or cat", "your coworkers", "your high school teacher",
    "a stranger watching you at the grocery store", "your phone", "your car", "your neighbors", "your siblings",
    "your boss", "your barista", "your childhood self", "your future self", "your kids", "your grandparents",
    "your Spotify history", "your search history", "your camera roll", "your closet"]
something_about = ["most people don't know", "that surprises people", "that you've changed in the last five years",
    "you'd never guess from looking at you", "that makes you unique", "you're working on", "you hope never changes",
    "your family always teases you about", "that would make a good headline", "that's on your bucket list"]
person_pairs = [("a morning", "a night"), ("a cat", "a dog"), ("a beach", "a mountains"), ("a coffee", "a tea"),
    ("a sweet", "a savory"), ("an early", "a just-on-time"), ("a planner", "a go-with-the-flow"), ("a city", "a country"),
    ("a summer", "a winter"), ("a text", "a phone-call"), ("a book", "a movie"), ("a sunrise", "a sunset"),
    ("a big-party", "a small-gathering"), ("a shower", "a bath"), ("a pie", "a cake"), 
    ("a details", "a big-picture"), ("a save", "a spend"), ("a road-trip", "a fly-there"), ("an indoor", "an outdoor")]
last_thing = ["thing you googled", "show you binged", "photo you took", "thing that made you laugh out loud", "book you read",
    "purchase you regretted", "concert you went to", "thing you cooked", "text you sent", "song you listened to",
    "time you tried something new", "time you got lost", "compliment you received", "gift you gave", "trip you took",
    "thing you fixed", "movie you saw in a theater", "time you danced", "new person you met", "thing you learned",
    "time you laughed so hard you cried", "risk you took", "thing you won", "app you downloaded", "time you were really proud",
    "handwritten note you got", "game you played", "meal you'd eat again", "thing you got rid of", "habit you started"]
whats_in = ["fridge", "car", "bag", "browser tabs", "camera roll", "junk drawer", "pockets", "nightstand", "desk drawer", "cart online"]
C["you"] = (
    T("What's your {x}?", whats_your)
    + T("How would {x} describe you?", describe_you)
    + T("What's something {x} about you?", something_about)
    + [f"Are you {a} person or {b} person?".replace("a details", "a details").replace("person or", "person or")
       for a, b in person_pairs]
    + T("What's the last {x}?", last_thing)
    + T("What's in your {x} right now?", whats_in)
    + lines("""
What are three words that describe you?
What's your origin story in 60 seconds?
What's something you're looking forward to?
What's the best decision you've made this year?
What's a small thing that made your week?
What's a habit you're proud of?
What's your go-to way to cheer yourself up?
What's the most 'you' thing you own?
What's something you're really good at but never get to show off?
What's something that always makes you laugh?
What's one thing you can't start your day without?
What's your favorite way to be celebrated?
What's the best compliment you've ever received?
What do people come to you for advice about?
What's one thing on your bucket list you'll definitely do?
What's something you used to hate but now love?
What's your favorite thing about where you live?
What's the best thing that happened to you this month?
What gets you out of bed in the morning?
What's a rule you live by?
"""))

# ------------------------------------------------------------------- Deep Talk
something_you = ["are proud of but rarely talk about", "changed your mind about recently", "wish you'd learned sooner",
    "are still figuring out", "believe that most people don't", "are grateful for today", "would tell a room full of teenagers",
    "want to be remembered for", "would do if you knew you couldn't fail", "are afraid of losing", "have forgiven",
    "have never said out loud", "want more of in your life", "want less of in your life", "learned from a failure",
    "learned from a loss", "wish more people understood about you", "find beautiful that others overlook",
    "hope your kids or the next generation get right", "would do differently if you started over",
    "are holding on to that you should let go", "keep putting off", "are quietly working toward",
    "admire in someone you disagree with", "do that makes you feel most like yourself", "would fight for",
    "used to believe about success", "know now that you didn't know a year ago", "are curious about lately",
    "want to get braver about", "look for in a friend", "find meaningful about your work", "consider a luxury",
    "think about more than you'd admit", "want to protect", "need to hear more often", "have outgrown",
    "are learning to accept", "hope people say about you", "would put in a time capsule", "find hard to ask for",
    "think makes a life well lived", "would tell your younger self about love", "think about when you can't sleep",
    "most want to experience before you die", "find comforting", "consider your greatest strength",
    "still carry from your childhood", "would change about how you spend your time", "wish you could say to someone you've lost"]
someone_who = ["shaped who you are", "you'd like to thank but never have", "believed in you before you did",
    "changed the way you see the world", "you admire quietly", "taught you how to love", "taught you how to work hard",
    "made a hard time easier", "you miss", "always makes you feel understood", "you lost touch with but think about",
    "showed you what courage looks like", "you'd want by your side in a crisis", "taught you to laugh at yourself",
    "inspires you to be better", "you look up to", "gave you a chance", "you'd like to know better", "made you feel brave",
    "you hope to become more like"]
means = ["success", "home", "friendship", "courage", "a good life", "rest", "faith", "family", "freedom", "love", "wealth",
    "integrity", "kindness", "growing up", "happiness", "legacy", "community", "adventure", "loyalty", "peace",
    "ambition", "forgiveness", "balance", "purpose", "beauty"]
advice_about = ["money", "love", "work", "parenting", "failure", "friendship", "health", "change", "grief", "fear",
    "marriage", "risk", "happiness", "conflict", "regret", "aging", "leadership", "patience", "starting over", "getting through a hard time"]
self_at = ["10", "15", "18", "21", "25", "30", "40"]
C["deep"] = (
    T("What's something you {x}?", something_you)
    + T("Who is someone who {x}?", someone_who)
    + T("What does {x} mean to you?", means)
    + T("What's the best advice you've ever received about {x}?", advice_about)
    + T("What would you tell your {x}-year-old self?", self_at)
    + lines("""
What's a moment that changed the direction of your life?
When do you feel most like yourself?
What's a belief you hold that's been tested?
What are you most grateful for right now?
What would you do with your life if money weren't a factor?
What's the bravest thing you've ever done?
What's a lesson you had to learn more than once?
What's the kindest thing a stranger has done for you?
What do you hope your life looks like in ten years?
What's something that's harder than it looks?
How do you want people to feel after spending time with you?
What's a tradition you want to keep alive?
What's the most important thing your parents taught you?
When was the last time you changed your mind about something big?
What's something you're still healing from?
What does a perfect ordinary day look like for you?
What's a question you wish people asked you more often?
What's the hardest goodbye you've ever had to say?
What's something you'd like to be forgiven for?
What does it mean to you to live a good life?
What's a fear you've overcome?
What's a dream you've let go of, and how do you feel about it now?
What's one thing you'd want everyone in this room to know about you?
What makes you feel truly at peace?
What's the best day of your life so far?
"""))

# ---------------------------------------------------------- Friendship & Family
most_likely = ["become famous", "survive a zombie apocalypse", "win a reality show", "get lost on a hike", "cry at a commercial",
    "start a business", "show up late to their own wedding", "adopt ten cats", "win the lottery and lose the ticket",
    "talk their way out of a speeding ticket", "move to another country", "forget their own birthday", "become a TikTok star",
    "eat something off the floor", "befriend a stranger on a plane", "run for office", "write a bestselling book",
    "get stuck in a revolving door", "plan the best party", "accidentally start a fire cooking", "laugh at the wrong moment",
    "know everyone's business", "give the best advice", "break something expensive", "remember everyone's birthday",
    "go viral by accident", "fall asleep at a party", "say yes to anything", "keep a secret forever", "end up on the news"]
learned_from = ["mom", "dad", "grandparents", "siblings", "best friend", "favorite teacher", "coach", "aunt or uncle", "kids",
    "first boss", "oldest friend", "neighbors"]
tradition_for = ["birthdays", "Thanksgiving", "the winter holidays", "New Year's", "summer", "Sunday dinners", "road trips",
    "the first day of school", "Halloween", "family reunions", "graduations", "game nights"]
C["family"] = (
    T("Who in your family is most likely to {x}?", most_likely)
    + T("Who in your friend group is most likely to {x}?", most_likely)
    + T("What's something you learned from your {x}?", learned_from)
    + T("What's a tradition your family has for {x}?", tradition_for)
    + lines("""
How did you meet your best friend?
Who's the funniest person in your family?
What's a family story that gets told at every gathering?
What's the best thing a friend has ever done for you?
What makes someone a great friend?
Who's the friend you've known the longest?
What's a family recipe you'd fight to protect?
What's something your family does that other families don't?
Who in your family are you most like?
What's the best advice a grandparent gave you?
What's your favorite memory with your siblings or cousins?
How do you and your friends keep in touch?
What's a friendship that changed your life?
What's your family's most-used inside joke?
How has your relationship with your parents changed as you've grown?
What's a family trip you'll never forget?
What's a quality you hope to pass down?
What's the most memorable family holiday you've had?
What's a lesson about friendship you learned the hard way?
Who would you call first with good news?
What's something you admire about someone in your family?
How do you show the people you love that you care?
What's a family name or heirloom with a story behind it?
What's the most fun you've ever had with friends?
What's something your family argues about every holiday?
What's a friend tradition you love?
Who in your life always shows up?
What do you wish you'd asked an older relative while you could?
What's something you want your family to know about you?
How would your friends describe your role in the group?
"""))

# ------------------------------------------------------------ Dating & Romance
opinion_on = ["splitting the check on a first date", "texting right after a date", "meeting online", "dating a coworker",
    "public displays of affection", "first-date kisses", "dating apps", "being friends with exes", "surprise dates",
    "love at first sight", "soulmates", "blind dates", "double dates", "meeting the parents early", "long-distance relationships",
    "Valentine's Day", "matching tattoos", "moving in together", "sharing passwords", "pet names", "jealousy",
    "grand romantic gestures", "following an ex on social media", "the three-date rule", "dating someone much older or younger"]
flag_in = ["on a first date", "in a dating profile", "in someone's apartment", "in how someone treats a server",
    "in someone's friend group", "in someone's text messages", "in someone's playlist", "in how someone talks about their ex",
    "in how someone handles a disagreement", "in how someone treats their family", "in someone's bookshelf", "in someone's car"]
first_date_for = ["a rainy day", "a tight budget", "a foodie", "an introvert", "a thrill-seeker", "a bookworm", "winter",
    "summer", "a big city", "a small town"]
date_spots = ["a coffee shop", "a museum", "a hiking trail", "a bowling alley", "a fancy dinner", "a comedy club",
    "a farmers market", "a concert", "a mini-golf course", "a cooking class", "a picnic in the park", "a trivia night",
    "an arcade", "a sunset boat ride"]
C["dating"] = (
    T("What's your opinion on {x}?", opinion_on)
    + T("What's a green flag {x}?", flag_in)
    + T("What's a red flag {x}?", flag_in)
    + T("What's the best first date idea for {x}?", first_date_for)
    + pairs("Would you rather go on a first date to {a} or {b}?", date_spots)
    + lines("""
What's the best date you've ever been on?
What's the worst date you've ever been on?
What's the first thing you notice about someone?
What's your ideal first date?
How do you know when you have a crush on someone?
What's the most romantic thing someone has done for you?
What's the most romantic thing you've done for someone?
What's a deal-breaker for you?
What's a small gesture that means a lot to you?
What's your love language?
What's the best pickup line you've ever heard?
Do you believe in love at first sight?
What's a romantic movie that set unrealistic expectations?
Who was your first crush?
What's your most embarrassing dating moment?
How do you like to be asked out?
What's the best relationship advice you've received?
What does a healthy relationship look like to you?
What's something you learned from a past relationship?
What's your idea of a perfect weekend with a partner?
What's the cheesiest romantic thing you secretly love?
What do you find most attractive in a person?
How long should you wait to say 'I love you'?
Who's a couple you admire, and why?
What's a love song that gets you every time?
What's the sweetest text you've ever received?
What's a date idea you've always wanted to try?
Are you a hopeless romantic or a realist?
What's your idea of a perfect proposal?
What's the best way to make up after a fight?
How do you show someone you're interested?
What's a quality you didn't know you needed in a partner until you found it?
What's your favorite love story, real or fictional?
What's the most spontaneous romantic thing you've done?
What makes you feel truly seen by someone?
"""))

# -------------------------------------------------------------- Couples Connect
mem_us = ["on vacation", "at a holiday", "from our first year", "at a wedding", "in the kitchen", "on a road trip",
    "from a time things were hard", "from a lazy Sunday", "from a night out", "from our early dates", "with our friends",
    "with family", "from a celebration", "outdoors", "from a rainy day", "from a time we laughed until we cried",
    "from a surprise", "from a big milestone", "from an ordinary weeknight", "that no one else knows about"]
feel_x = ["loved", "safe", "seen", "appreciated", "respected", "chosen", "calm", "proud", "supported", "understood", "desired",
    "cared for", "at home", "lucky", "playful", "heard", "special", "valued", "confident", "adored"]
support_when = ["stressed", "sad", "tired", "overwhelmed", "anxious", "sick", "angry", "disappointed", "grieving", "nervous",
    "frustrated", "lonely", "discouraged", "burned out", "unsure of yourself"]
love_to_us = ["try together this year", "do more often", "start as a tradition", "learn together", "plan for the future",
    "do on our next vacation", "change about our routine", "celebrate more", "talk about more openly", "spend money on together",
    "build together", "make time for", "say to each other more", "do on a free Saturday", "create in our home"]
see_us = ["in five years", "in ten years", "when we retire", "next summer", "a year from now", "in twenty years"]
fav_our = ["home", "weekends", "inside jokes", "mornings", "friendship", "conversations", "traditions", "teamwork",
    "dates", "trips", "rituals before bed", "way of making up", "story of how we met", "kitchen", "shared music",
    "laughs", "quiet moments", "adventures", "differences", "future plans"]
perfect_our = ["Sunday", "date night", "vacation", "anniversary", "holiday", "snow day", "birthday", "road trip", "rainy day",
    "summer evening", "weekend away", "morning", "night in", "picnic", "staycation", "dinner party", "fall afternoon",
    "beach day", "New Year's Eve", "lazy afternoon"]
rate_us = ["communication", "date nights", "dividing chores", "making time for fun", "handling conflict",
    "supporting each other's goals", "saying thank you", "managing money together", "physical affection", "listening",
    "trying new things", "keeping romance alive", "giving each other space", "showing appreciation", "planning ahead",
    "being silly together", "apologizing", "celebrating each other", "unplugging from phones", "talking about the future"]
never_told = ["your childhood", "your first love", "your fears", "your dreams", "the day we met", "your family",
    "a time you were proud of me", "something you want to try", "a secret talent", "what you were thinking on our first date",
    "a goal you haven't shared", "something that scares you about the future"]
first_when = ["realize you loved me", "feel at home with me", "notice you were falling for me", "feel like we were a team",
    "know you wanted a future with me", "laugh so hard with me you cried", "feel nervous around me", "want to introduce me to your family",
    "feel completely comfortable being yourself with me", "think 'this is the one'", "miss me", "feel proud to be with me",
    "see me at my worst and stay", "imagine growing old with me", "say 'we' instead of 'I'"]
C["couples"] = (
    T("What's your favorite memory of us {x}?", mem_us)
    + T("What's something I do that makes you feel {x}?", feel_x)
    + T("How can I better support you when you're {x}?", support_when)
    + T("What's one thing you'd love for us to {x}?", love_to_us)
    + T("Where do you see us {x}?", see_us)
    + T("What's your favorite thing about our {x}?", fav_our)
    + T("What would our perfect {x} together look like?", perfect_our)
    + T("On a scale of 1 to 10, how are we doing at {x}? What would make it a 10?", rate_us)
    + T("What's something about {x} you've never told me?", never_told)
    + T("When did you first {x}?", first_when)
    + lines("""
What was your first impression of me?
What's something you've learned from me?
What's one thing I do that always makes you smile?
What's a habit of mine you secretly love?
What's a habit of mine you could do without?
What song reminds you of us?
What's our best inside joke?
What's a moment you were proudest to be with me?
What's a dream you have that I can help with?
What's something we've overcome together that made us stronger?
How do you like to be loved on a hard day?
What's a small thing I could do every day that would mean a lot?
What's something you'd like us to do more of?
What's something new you'd like to try together?
What's your favorite photo of us?
What's a tradition you want us to keep forever?
What's one thing you want me to know about how you're feeling lately?
What's a way I've changed you for the better?
What's a fight we had that you're glad we had?
What part of our life together do you never want to change?
What's a goal you want us to set together this year?
What do you think we're best at as a couple?
What do you think we could work on as a couple?
What do you appreciate about me that you don't say often enough?
What's the best gift I've ever given you?
What's a memory from our early days that still makes you laugh?
What's something you'd want our future selves to remember about this season of life?
What's a place you'd love for us to go together?
How do you know when I need a hug?
What's a question you've always wanted to ask me?
What would you write in a love letter to me right now?
What's one way I make your life easier?
What does a perfect day off together look like to you?
What's something you'd like to celebrate about us?
What's one promise you'd like us to make to each other?
"""))

# ----------------------------------------------------------------- Intimacy
feel_most = ["close", "connected", "desired", "safe", "relaxed", "beautiful", "wanted", "comfortable", "playful", "vulnerable",
    "secure", "attractive", "cherished", "at ease", "present"]
fav_kind = ["hug", "kiss", "cuddle", "touch", "compliment", "date", "love note", "surprise", "morning together", "quiet evening",
    "slow dance", "goodnight ritual"]
more_of = ["affection", "praise", "quality time", "physical touch", "words of affirmation", "surprises", "help around the house",
    "undivided attention", "eye contact", "slow mornings", "romantic gestures", "spontaneity"]
like_be = ["comforted", "kissed", "held", "surprised", "flirted with", "celebrated", "cared for when you're sick", "apologized to",
    "greeted at the end of the day", "woken up", "complimented", "pursued", "reassured", "touched when you're stressed",
    "loved after a long day"]
mean_rel = ["intimacy", "trust", "vulnerability", "passion", "commitment", "romance", "closeness", "desire", "safety",
    "loyalty", "respect", "partnership"]
C["intimacy"] = (
    T("When do you feel most {x} with me?", feel_most)
    + T("What's your favorite kind of {x} from me?", fav_kind)
    + T("What kind of {x} would you love more of from me?", more_of)
    + T("How do you most like to be {x}?", like_be)
    + T("What does {x} mean to you in a relationship?", mean_rel)
    + lines("""
What's the most intimate moment we've shared that didn't involve words?
When did you first feel truly vulnerable with me?
What's something you've been wanting to tell me but haven't found the right moment for?
What's a fear you have about our relationship that you've never said out loud?
How can I make you feel more desired?
What's something that makes you feel closer to me after a disagreement?
What's a part of yourself you're still learning to share with me?
What does a perfect evening alone together look like to you?
What's the most romantic moment of our relationship so far?
What's one thing I do that instantly makes you feel loved?
How has our intimacy changed since we first got together?
What's something you'd like us to slow down and savor more?
What's a way you'd like me to show affection in public?
What's a way you'd like me to show affection in private?
What makes you feel most connected to me during a busy week?
What's a memory of us that still gives you butterflies?
What do you need from me when you're feeling disconnected?
What's a touch of mine that calms you down?
What's a compliment from me that has stayed with you?
How do you like to reconnect after time apart?
What's something about your body you'd like me to appreciate more?
What makes you feel safe enough to be completely yourself with me?
What's something new you'd like to experience together?
How can we protect time for just the two of us?
What's a moment you felt deeply understood by me?
What's a way we could be more playful with each other?
What helps you feel relaxed enough to be close?
What's something romantic you've always wanted but never asked for?
When do you feel most attracted to me?
What's your favorite way to fall asleep together?
What's your favorite way to wake up together?
What does feeling cherished look like for you?
What's one thing that would make our time together feel more special?
What's something about me that you find beautiful that I might not see?
What's a love language you wish I spoke more fluently?
How do you want to be held when you're upset?
What's a moment you wished I had reached for you?
What's something you love about the way I look at you?
What's a boundary that helps you feel safe with me?
What does trust feel like in your body?
How do you like me to ask for closeness?
What's a small ritual that could make us feel closer every day?
What's the most meaningful thing I've ever whispered to you?
What would you like more of when we're alone together?
What do you think keeps a long-term relationship passionate?
What's a song that makes you want to slow dance with me?
How do you feel when I hold your hand?
What's an unspoken way I tell you I love you?
What's a way I can show you I'm thinking about you during the day?
What do you want our relationship to feel like ten years from now?
"""))

# --------------------------------------------------------------- Flirty (after dark)
attractive_my = ["smile", "laugh", "eyes", "voice", "hands", "style", "confidence", "mind", "sense of humor", "kindness",
    "energy", "walk", "cologne or perfume", "dance moves", "cooking"]
rate_skills = ["flirting", "slow dancing", "pickup lines", "giving massages", "writing love notes", "cooking a romantic dinner",
    "setting the mood", "making eye contact across a room", "kissing", "planning surprise dates", "sending flirty texts",
    "whispering sweet nothings"]
kiss_spots = ["in the rain", "on a Ferris wheel", "under fireworks", "on a beach at sunset", "on a mountaintop", "in a dark movie theater",
    "in the kitchen while dinner burns", "under mistletoe", "on a rooftop", "in the middle of a dance floor", "in the back of a cab",
    "in a quiet library aisle", "in a hot-air balloon", "on a snowy street", "at a crowded concert"]
three_words = ["date night", "kiss", "evening in", "weekend away", "first impression of me", "favorite outfit of mine",
    "perfect morning together", "getaway", "dream hotel room", "slow dance"]
flirt_where = ["at a party", "over text", "at a bar", "on a plane", "on a first date", "in a grocery store", "at a wedding",
    "on vacation", "at a concert", "in a coffee shop"]
C["spicy"] = (
    T("What's the most attractive thing about my {x}?", attractive_my)
    + T("Rate your {x} skills from 1 to 10. Then prove it.", rate_skills)
    + pairs("Would you rather be kissed {a} or {b}?", kiss_spots)
    + T("Describe your ideal {x} in three flirty words.", three_words)
    + T("What's the boldest flirting you've ever done {x}?", flirt_where)
    + lines("""
What's the first thing you noticed about me physically?
What outfit of mine is your favorite?
What's a compliment that would make you blush?
What's something I do that drives you wild, in a good way?
What's your favorite kind of kiss?
Have you ever had a dream about me? Tell me about it.
What's one thing you'd like me to whisper to you?
What's the most memorable kiss we've shared?
Where's the most unexpected place you've wanted to kiss me?
What's the flirtiest text you've ever sent?
What's a look I give you that you can't resist?
What's your idea of a perfect romantic getaway?
What's the best kiss you've ever had in a movie scene?
What's a song that puts you in the mood for romance?
What would you plan for a date night that ends with us staying in?
What's a fantasy date you've never told me about?
What's the most attractive thing someone can do without even trying?
What's your favorite thing about the way I kiss you?
Where's your favorite place to be touched, like on your neck, hands, or back?
What's the most seductive scent in the world?
What's a pet name you'd secretly love for me to call you?
If we had a whole weekend alone with no plans, how would you want to spend it?
What's something you'd love to try together that you've been shy to bring up?
What's a moment you couldn't keep your hands off me?
What's your favorite memory of us dressed up?
What's your favorite memory of us dressed down?
What's the most romantic thing you've ever imagined us doing?
What's your favorite way to be teased?
Would you rather slow dance in the kitchen or skinny-dip under the stars?
What's one thing I wear that you think is irresistible?
What's the most romantic hotel room you can imagine?
What's a flirty dare you'd give me right now?
What would your perfect love note from me say?
What's a little thing I do that turns you on?
What's your favorite way to start a romantic evening?
Truth: What's the most daring thing you've done for love?
What's a movie scene you'd want to recreate with me?
What's something about me that you think about when I'm not around?
What's the sexiest thing about confidence?
What's your favorite time of day to be close to me?
What's a secret you'd only tell me after midnight?
Would you rather have a candlelit bath together or a massage night?
What's the most attractive thing I've ever said to you?
What's your weakness when it comes to flirting?
What's a playful game we could play on date night?
How would you seduce me with just three words?
What's something you've always wanted me to wear?
What's one thing you'd love me to surprise you with in the bedroom?
If you could plan our steamiest date night, where would it start?
What's a slow-burn moment between us you still think about?
"""))


# ---------------------------------------------------------------- Top-ups
C["pop"] += T("What's your favorite {x}?", ["'80s movie", "'90s movie", "Pixar movie", "Disney song", "Beatles song", "TV theme song",
    "holiday song", "musical", "late-night host", "game show", "podcast", "movie quote", "concert you've attended", "show streaming right now",
    "TV dad", "TV mom", "movie couple", "action hero", "movie franchise", "song from high school", "movie score", "music festival",
    "road trip album", "fictional detective", "sitcom character"])
C["pop"] += pairs("Which is better: {a} or {b}?", ["Star Wars", "Star Trek", "Marvel", "DC", "Harry Potter", "The Lord of the Rings",
    "Jurassic Park", "Indiana Jones", "Back to the Future", "Toy Story", "James Bond", "Rocky", "Mission: Impossible", "Shrek"])
C["whatif"] += T("If you could live in any {x}, which would you pick?", ["decade", "city", "fictional world", "country",
    "house from a movie", "era of history", "climate", "planet", "book", "video game"])
C["whatif"] += T("What would you do if you {x}?", ["won the lottery tomorrow", "were president for a day", "found a wallet with $1,000 in it",
    "could stop aging", "ran into your favorite celebrity", "had to move abroad next month", "could quit your job today",
    "found a secret room in your house", "got stuck in an elevator with a celebrity", "could read your pet's mind",
    "woke up 20 years in the future", "met your clone", "discovered a new island", "got a call from NASA", "inherited a castle",
    "could relive high school", "met an alien", "could only speak in questions for a day", "became mayor of your town", "shrank to six inches tall"])
C["you"] += T("What's your {x}?", ["favorite compliment to give", "biggest accomplishment", "go-to road trip snack", "favorite way to exercise",
    "all-time favorite purchase", "favorite thing to wear", "favorite smell from childhood", "go-to party trick", "dream vacation",
    "favorite weekend ritual", "most treasured memory", "favorite game", "favorite thing to cook", "best advice in one sentence",
    "favorite time of year", "favorite place to think", "most-used emoji", "favorite way to relax", "proudest skill", "comfort song"])
C["you"] += lines("""
Are you more of a leader or a follower?
Are you more of a talker or a listener?
Are you more of a saver or a spender?
Are you more spontaneous or more of a planner?
Are you more of a homebody or an adventurer?
Are you more of a thinker or a doer?
Are you more of a giver or a receiver?
Are you more competitive or more cooperative?
Are you more of a starter or a finisher?
Are you more introverted or extroverted?
Are you more of an optimist or a realist?
Are you more of a minimalist or a collector?
Are you more of a head person or a heart person?
Are you more of a big-group person or a one-on-one person?
Are you more of a routine person or a variety person?
Are you more of a risk-taker or a play-it-safe person?
Are you more of a city mouse or a country mouse?
Are you more of a fixer or a listener when a friend is upset?
Are you more of a list-maker or a keep-it-in-your-head person?
Are you more of a sunrise person or a sunset person?
""")
C["deep"] += T("What's a moment when you felt {x}?", ["truly proud", "deeply grateful", "completely free", "really brave", "totally at peace",
    "seen by someone", "out of your depth", "like a grown-up for the first time", "part of something bigger", "really lucky",
    "forgiven", "fully alive", "most like yourself", "homesick", "inspired", "connected to nature", "close to your family",
    "proud of someone else", "understood", "hopeful"])
C["deep"] += T("How has your view of {x} changed over the years?", means)
C["family"] += T("Who in your family {x}?", ["gives the best hugs", "tells the best stories", "is the best cook", "is the family historian",
    "would win a talent show", "always hosts", "is the peacemaker", "is the most competitive", "is the best gift-giver",
    "texts in all caps", "is always running late", "gives the best advice", "has the loudest laugh", "would survive in the wild",
    "is the biggest sports fan", "has the best taste in music", "is the most sentimental", "is the jokester", "is the planner",
    "is most like you"])
C["family"] += T("What's your favorite memory with your {x}?", learned_from)
C["intimacy"] += T("What's one way I could make you feel more {x}?", feel_most)
C["intimacy"] += T("What's a moment you felt especially {x} with me?", feel_most)
C["wyr"] += pairs("Would you rather have dinner with {a} or {b}?", ["Abraham Lincoln", "Theodore Roosevelt", "Cleopatra",
    "Leonardo da Vinci", "Albert Einstein", "Amelia Earhart", "Marie Curie", "William Shakespeare", "Benjamin Franklin",
    "Mark Twain", "Harriet Tubman", "Napoleon"])

# ---------------------------------------------------------------------- Output
CATS = [
    ("fun", "Just for Fun", "Hot takes and silly stuff", "#ff7a59", 0),
    ("wyr", "Would You Rather", "Pick your poison", "#7c5cff", 0),
    ("picks", "Quick Picks", "This or that, rank these", "#00a6a6", 0),
    ("food", "Food & Drink", "Cravings and kitchen stories", "#e8a317", 0),
    ("travel", "Travel & Places", "Trips, maps and bucket lists", "#2a8bdc", 0),
    ("kid", "Childhood", "Nostalgia and growing up", "#f25c94", 0),
    ("work", "Work & Career", "Jobs, bosses and big wins", "#4c6ef5", 0),
    ("whatif", "What If", "Wild hypotheticals", "#9b51e0", 0),
    ("pop", "Movies, Music & TV", "Pop culture and playlists", "#e5484d", 0),
    ("hobby", "Hobbies & Skills", "Things you make and do", "#30a46c", 0),
    ("you", "All About You", "Quirks, habits and you", "#f76b15", 0),
    ("deep", "Deep Talk", "Values and turning points", "#3e63dd", 0),
    ("family", "Friends & Family", "Your people", "#d6409f", 0),
    ("dating", "Dating & Romance", "Crushes and first dates", "#e54666", 1),
    ("couples", "Couples Connect", "For partners", "#c2298a", 1),
    ("intimacy", "Intimacy", "Closeness and trust", "#a1255b", 1),
    ("spicy", "Flirty", "Turn up the heat", "#d13415", 1),
]

def clean(q):
    q = re.sub(r"\s+", " ", q).strip()
    q = q.replace("a(n) a", "an a").replace("a(n) e", "an e").replace("a(n) i", "an i").replace("a(n) o", "an o").replace("a(n) u", "an u").replace("a(n) ", "a ")
    q = re.sub(r"\b([Aa]) ([aeiouAEIOU])", lambda m: m.group(1) + "n " + m.group(2), q)
    q = q.replace("an uni", "a uni").replace("an use", "a use").replace("an one", "a one").replace("an Ute", "a Ute")
    return q[0].upper() + q[1:]

seen, out, total = set(), {}, 0
for cid, *_ in CATS:
    qs = []
    for q in C[cid]:
        q = clean(q)
        k = q.lower()
        if k not in seen:
            seen.add(k); qs.append(q)
    out[cid] = qs
    total += len(qs)

meta = [{"id": c, "name": n, "tag": t, "color": col, "adult": a, "count": len(out[c])} for c, n, t, col, a in CATS]
root = pathlib.Path(__file__).resolve().parent.parent
js = "// Generated by tools/build_questions.py. Edit that file, not this one.\n"
js += "window.ICEBREAKER = " + json.dumps({"cats": meta, "q": out}, ensure_ascii=False, separators=(",", ":")) + ";\n"
(root / "questions.js").write_text(js, encoding="utf-8")
for m in meta:
    print(f"{m['name']:22} {m['count']:5}")
print("TOTAL", total)
