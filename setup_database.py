import mysql.connector
import hashlib
import time
from mysql.connector import errorcode

# Database connection config
DB_CONFIG = {
    'user': 'root',
    'password': 'admin',  # <-- CHANGE PASSWORD if needed
    'host': '127.0.0.1'
}

DB_NAME = 'bitechain_db'

# -------------------- TABLE DEFINITIONS --------------------
TABLES = {}

TABLES['users'] = """
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE
    )
"""

TABLES['restaurants'] = """
    CREATE TABLE restaurants (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        cuisine VARCHAR(50),
        vibe VARCHAR(25),
        cost VARCHAR(20),
        location VARCHAR(255),
        image_url VARCHAR(255),
        tags VARCHAR(700),
        is_local TINYINT(1) DEFAULT 0,
        dietary_info VARCHAR(255),
        fitness_info VARCHAR(255)
    )
"""

TABLES['reviews'] = """
    CREATE TABLE reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        restaurant_id INT,
        user_id INT,
        rating INT NOT NULL,
        feedback_text TEXT,
        creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        verifications INT DEFAULT 0,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
"""

TABLES['blockchain'] = """
    CREATE TABLE blockchain (
        id INT PRIMARY KEY,
        timestamp BIGINT,
        review_id INT,
        previous_hash VARCHAR(64),
        nonce INT,
        hash VARCHAR(64),
        FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
    )
"""

TABLES['restaurant_tags'] = """
    CREATE TABLE restaurant_tags (
        id INT AUTO_INCREMENT PRIMARY KEY,
        restaurant_id INT,
        tag_name VARCHAR(100) NOT NULL,
        votes INT DEFAULT 0,
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
    )
"""

# -------------------- INITIAL DATA --------------------
DATA = {}

DATA['users'] = """
    INSERT INTO users (id, username)
    VALUES
        (1, 'alex'),
        (2, 'jyoti'),
        (3, 'casey'),
        (4, 'suresh')
"""

# Restaurants: Final & Mapped
DATA['restaurants'] = """
    INSERT INTO restaurants (id, name, cuisine, vibe, cost, location, image_url, tags, is_local, dietary_info, fitness_info) VALUES
    (1, 'Saravana Bhavan', 'South Indian', 'Family', '₹400-₹1000', 'T. Nagar, Chennai', 'https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg', 'dosa,idli,vada,pongal,thali,sambar,filter-coffee,poori,kesari,uthappam,chole-bhature,ice-cream,lassi,juice,tea,gulab-jamun,jalebi,bisibele-bath,salad', 1, 'vegetarian,vegan-options', 'low-carb'),
    (2, 'Dindigul Thalappakatti', 'Biryani', 'Casual', '₹500-₹1200', 'Guindy, Chennai', 'https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg', 'mutton-biryani,chicken-biryani,karandi-omlette,chicken-65,parotta,mutton-sukka,falooda,kebab,tandoori-chicken,butter-chicken,fish-fry,naan,dal-makhani,lassi', 1, '', 'high-protein'),
    (3, 'Toscana Pizzeria', 'Italian', 'Trendy', '₹800-₹2000', 'Besant Nagar, Chennai', 'https://images.pexels.com/photos/1566837/pexels-photo-1566837.jpeg', 'pizza,lasagna,tiramisu,pasta,garlic-bread,ravioli,panna-cotta,bruschetta,risotto,mocktails,salad,soup,cheesecake,tacos', 0, 'gluten-free-options', ''),
    (4, 'MTR - Mavalli Tiffin Rooms', 'South Indian', 'Historic', '₹300-₹700', 'Lalbagh Road, Bangalore', 'https://images.pexels.com/photos/5560763/pexels-photo-5560763.jpeg', 'rava-idli,masala-dosa,bisibele-bath,kesari-bath,filter-coffee,vada,chandrahara,poori-sagu,idli,sambar,jalebi', 1, 'vegetarian', ''),
    (5, 'Truffles', 'American', 'Lively', '₹500-₹1200', 'Koramangala, Bangalore', 'https://images.pexels.com/photos/1639562/pexels-photo-1639562.jpeg', 'burger,ferrero-rocher-shake,peri-peri-chicken-burger,wedges,pasta,steak,sizzler,sandwiches,fries,cheesecake,ice-cream,brownie,milkshake', 1, '', 'high-protein'),
    (6, 'Nagarjuna', 'Andhra', 'Family', '₹600-₹1500', 'Residency Road, Bangalore', 'https://images.pexels.com/photos/2474661/pexels-photo-2474661.jpeg', 'andhra-meals,mutton-biryani,chicken-roast,guntur-chicken,pappu,gongura,kodi-vepudu,fish-fry,biryani,fried-rice,thali', 0, '', 'high-protein'),
    (7, 'Leopold Cafe', 'Multi-Cuisine', 'Iconic', '₹1000-₹2500', 'Colaba, Mumbai', 'https://images.pexels.com/photos/1126728/pexels-photo-1126728.jpeg', 'beef-chilli,chicken-tikka,pasta,beer,cheesecake,tandoori-chicken,noodles,sandwiches,kingfisher,chilli-paneer,manchurian,soup,butter-chicken,dal-makhani', 1, '', ''),
    (8, 'Britannia & Co.', 'Parsi', 'Vintage', '₹800-₹1500', 'Ballard Estate, Mumbai', 'https://images.pexels.com/photos/604969/pexels-photo-604969.jpeg', 'berry-pulao,sali-boti,caramel-custard,dhansak,patra-ni-macchi,raspberry-soda,mutton-cutlet,samosa,ice-cream,biryani', 1, '', 'high-protein'),
    (9, 'Bademiya', 'Mughlai', 'Street Food', '₹400-₹1000', 'Colaba, Mumbai', 'https://images.pexels.com/photos/6209493/pexels-photo-6209493.jpeg', 'seekh-kebab,rumali-roti,chicken-bhuna,baida-roti,kheema-pav,tandoori-chicken,mutton-roll,butter-chicken,naan,dal-makhani,paneer-tikka,shawarma', 0, '', 'high-protein'),
    (10, 'Aki Bay', 'Japanese', 'Modern', '₹1200-₹3000', 'Bandra, Mumbai', 'https://images.pexels.com/photos/8951497/pexels-photo-8951497.jpeg', 'sushi,sashimi,ramen,tempura,miso-soup,edamame,teriyaki-chicken,seafood,fish,prawns,crab,noodles,momos,fried-rice', 0, '', 'high-protein')
    
    ,(11, 'Punjabi Dhaba', 'North Indian', 'Rustic', '₹300-₹900', 'NH44, Haryana', 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg',
    'butter-chicken,dal-makhani,roti,lassi,aloo-paratha,tandoori-chicken,rajma-chawal,paneer-butter-masala,gajar-ka-halwa', 1, 'vegetarian-options', 'high-protein'),
    (12, 'Mainland China', 'Chinese', 'Classic', '₹800-₹1800', 'Park Street, Kolkata', 'https://images.pexels.com/photos/2955820/pexels-photo-2955820.jpeg',
    'hakka-noodles,chilli-chicken,manchow-soup,crispy-chilli-babycorn,spring-rolls,hot-and-sour-soup,dimsum,dragon-chicken,fried-rice', 0, '', ''),
    (13, 'Bombay Canteen', 'Modern Indian', 'Trendy', '₹1200-₹2500', 'Lower Parel, Mumbai', 'https://images.pexels.com/photos/67468/pexels-photo-67468.jpeg',
    'tandoori-tacos,keema-pav,sev-puri-twist,craft-cocktails,seasonal-thali,fish-curry,tandoori-prawns,misal-pav,shrimp-pakora', 0, '', ''),
    (14, 'Olive Bar & Kitchen', 'Mediterranean', 'Luxury', '₹2000-₹4000', 'Mehrauli, Delhi', 'https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg',
    'mezze-platter,wood-fired-pizza,pasta,bruschetta,risotto,grilled-fish,cheesecake,wine,steak', 0, 'gluten-free-options', ''),
    (15, 'Karavalli', 'Coastal Karnataka', 'Heritage', '₹1000-₹2500', 'Residency Road, Bangalore', 'https://images.pexels.com/photos/539451/pexels-photo-539451.jpeg',
    'neer-dosa,fish-curry,mangalorean-prawn,crab-sukha,kori-rotti,appam,meenu-gassi,chicken-ghee-roast,seafood-thali', 1, '', 'high-protein'),
    (16, 'Paradise Biryani', 'Hyderabadi', 'Family', '₹600-₹1500', 'Secunderabad, Hyderabad', 'https://images.pexels.com/photos/11170284/pexels-photo-11170284.jpeg',
    'chicken-biryani,mutton-biryani,double-ka-meetha,mirchi-ka-salan,kebabs,rumali-roti,dalcha,bagara-rice,phirni', 1, '', 'high-protein'),
    (17, 'Kailash Parbat', 'Sindhi', 'Casual', '₹400-₹900', 'Colaba, Mumbai', 'https://images.pexels.com/photos/1435895/pexels-photo-1435895.jpeg',
    'pani-puri,sev-puri,dahi-puri,chole-bhature,sindhi-kadhi,dal-pakwaan,falooda,ragda-pattice,bhel-puri', 1, 'vegetarian', ''),
    (18, 'SodaBottleOpenerWala', 'Irani Cafe', 'Quirky', '₹600-₹1500', 'Cyber Hub, Gurgaon', 'https://images.pexels.com/photos/291958/pexels-photo-291958.jpeg',
    'bun-maska,irani-chai,berry-pulao,salli-boti,egg-kejriwal,kheema-pav,pudding,raspberry-soda,chicken-farcha', 0, '', ''),
    (19, 'Oh! Calcutta', 'Bengali', 'Classic', '₹800-₹2000', 'Elgin Road, Kolkata', 'https://images.pexels.com/photos/1640771/pexels-photo-1640771.jpeg',
    'ilish-bhapa,cholar-dal,shukto,kosha-mangsho,luchi,rosogolla,mishti-doi,chingri-malaikari,patishapta', 1, '', ''),
    (20, 'BBQ Nation', 'Multi-Cuisine', 'Lively', '₹1200-₹2500', 'Indiranagar, Bangalore', 'https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg',
    'barbeque-chicken,paneer-tikka,kebabs,grilled-prawns,dessert-spread,ice-cream,dal-makhani,biryani,chicken-wings', 0, '', 'high-protein')


    ,(21, 'Indian Accent', 'Modern Indian', 'Luxury', '₹2500-₹5000', 'Lodhi Road, Delhi', 'https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg',
    'daulat-ki-chaat,meetha-aachar,kokum-sherbet,paneer-tikka,fusion-thali,duck-korma,dal-makhani,roti,rasmalai', 0, 'vegetarian-options', ''),
    (22, 'Farzi Cafe', 'Fusion', 'Trendy', '₹1500-₹3000', 'Connaught Place, Delhi', 'https://images.pexels.com/photos/67468/pexels-photo-67468.jpeg',
    'dal-chawal-arancini,rajma-galouti,tandoori-chicken,smoked-cocktails,churros,parle-g-cheesecake,paneer-tikka,chaat', 0, '', ''),
    (23, 'Mamagoto', 'Pan-Asian', 'Casual', '₹1200-₹2500', 'Indiranagar, Bangalore', 'https://images.pexels.com/photos/2955820/pexels-photo-2955820.jpeg',
    'sushi,ramen,katsu-curry,dim-sums,noodles,pad-thai,laksa,stir-fry,teppanyaki', 0, '', 'high-protein'),
    (24, 'Barbeque Hut', 'Multi-Cuisine', 'Lively', '₹1000-₹2000', 'Banjara Hills, Hyderabad', 'https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg',
    'bbq-chicken,grilled-paneer,kebabs,fish-tikka,chicken-wings,naan,pasta,dal,ice-cream', 1, '', 'high-protein'),
    (25, 'Cafe Mondegar', 'Continental', 'Retro', '₹800-₹1800', 'Colaba, Mumbai', 'https://images.pexels.com/photos/1126728/pexels-photo-1126728.jpeg',
    'beer,burger,pasta,french-fries,omelette,club-sandwich,pizza,iced-tea,cheesecake', 1, '', ''),
    (26, 'Peter Cat', 'Anglo-Indian', 'Classic', '₹1000-₹2200', 'Park Street, Kolkata', 'https://images.pexels.com/photos/1640771/pexels-photo-1640771.jpeg',
    'chelo-kebab,chicken-tikka,fish-meal,veg-curry,biryani,dal,naan,paneer,ice-cream', 1, '', ''),
    (27, 'Biryani by Kilo', 'Biryani', 'Casual', '₹600-₹1500', 'Multiple Locations, India', 'https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg',
    'hyderabadi-biryani,kolkata-biryani,chicken-65,mutton-seekh,kebabs,rumali-roti,mirchi-ka-salan', 0, '', 'high-protein'),
    (28, 'Mahesh Lunch Home', 'Seafood', 'Family', '₹1500-₹3000', 'Juhu, Mumbai', 'https://images.pexels.com/photos/539451/pexels-photo-539451.jpeg',
    'prawn-gassi,crab-curry,fish-fry,tandoori-crab,appam,neer-dosa,kori-rotti,biryani,seafood-thali', 1, '', 'high-protein'),
    (29, 'Gunpowder', 'Kerala', 'Rustic', '₹800-₹2000', 'Assagao, Goa', 'https://images.pexels.com/photos/2474661/pexels-photo-2474661.jpeg',
    'appam,stew,puttu,kappa,meen-curry,beef-fry,fish-thali,prawn-curry,kerala-parotta', 1, 'gluten-free-options', 'high-protein'),
    (30, 'La Pinoz Pizza', 'Italian', 'Casual', '₹500-₹1200', 'Ahmedabad, Gujarat', 'https://images.pexels.com/photos/1566837/pexels-photo-1566837.jpeg',
    'pizza,garlic-bread,pasta,mozzarella-sticks,lasagna,salad,tacos,cheesecake', 0, 'vegetarian-options', '')

    """
DATA['reviews'] = """
    INSERT INTO reviews (restaurant_id, user_id, rating, feedback_text)
    VALUES
        (1, 1, 5, 'Best dosa in town!'),
        (4, 2, 5, 'Rava Idli is a must-try.'),
        (9, 3, 4, 'Legendary kebabs, perfect late night food.'),
        (10, 4, 5, 'Incredibly fresh sushi!')
"""

DATA['poll_tags'] = """
    INSERT INTO restaurant_tags (restaurant_id, tag_name, votes)
    VALUES
        (1, 'Authentic Filter Coffee', 35),
        (1, 'Perfect Ghee Roast Dosa', 28),
        (1, 'Great for Families', 22),
        (2, 'Best Mutton Biryani', 45),
        (2, 'Spicy Chicken 65', 38),
        (2, 'Value for Money', 30),
        (3, 'Wood-fired Pizzas', 29),
        (3, 'Romantic Ambiance', 23),
        (3, 'Delicious Tiramisu', 17),
        (4, 'Legendary Rava Idli', 42),
        (4, 'Historic Bangalore Vibe', 35),
        (4, 'Unforgettable Bisibele Bath', 28),
        (5, 'Juiciest Burgers', 38),
        (5, 'Thick Milkshakes', 31),
        (5, 'Popular with Students', 26),
        (6, 'Spicy Andhra Meals', 40),
        (6, 'Flavorful Biryani', 32),
        (6, 'Must-try Mutton Roast', 25),
        (7, 'Iconic Mumbai Spot', 35),
        (7, 'Great Beer Selection', 28),
        (7, 'Perfect for People Watching', 20),
        (8, 'Famous Berry Pulao', 48),
        (8, 'Vintage Parsi Decor', 39),
        (8, 'Caramel Custard is Heaven', 32),
        (9, 'Best Seekh Kebabs', 50),
        (9, 'Late Night Food Hub', 41),
        (9, 'Melt-in-mouth Rumali Roti', 35),
        (10, 'Freshest Sushi in Town', 40),
        (10, 'Authentic Ramen', 33),
        (10, 'Modern Japanese Decor', 25),
        (11, 'Best Butter Chicken', 40),
        (11, 'Authentic Punjabi Vibes', 32),
        (11, 'Perfect Tandoori Roti', 25),
        (12, 'Authentic Chinese Flavors', 38),
        (12, 'Best Chilli Chicken', 30),
        (12, 'Crispy Spring Rolls', 22),
        (13, 'Creative Indian Fusion', 35),
        (13, 'Must-try Keema Pav', 28),
        (13, 'Trendy Mumbai Spot', 20),
        (14, 'Romantic Ambiance', 45),
        (14, 'Best Mediterranean Platters', 36),
        (14, 'Great Wine Selection', 27),
        (15, 'Authentic Coastal Flavors', 40),
        (15, 'Best Fish Curry', 33),
        (15, 'Traditional Mangalorean Vibe', 25),
        (16, 'Legendary Hyderabadi Biryani', 50),
        (16, 'Best Double ka Meetha', 42),
        (16, 'Spicy Mirchi ka Salan', 30),
        (17, 'Famous Chaat Items', 39),
        (17, 'Delicious Falooda', 31),
        (17, 'Authentic Sindhi Flavors', 24),
        (18, 'Quirky Irani Cafe', 37),
        (18, 'Best Bun Maska & Chai', 29),
        (18, 'Berry Pulao is a Hit', 21),
        (19, 'Best Bengali Sweets', 45),
        (19, 'Authentic Kosha Mangsho', 38),
        (19, 'Traditional Kolkata Dining', 28),
        (20, 'Unlimited BBQ Feast', 50),
        (20, 'Best Kebabs in Town', 42),
        (20, 'Great for Groups', 35)
"""

# -------------------- GENESIS BLOCK --------------------
def create_genesis_block(cursor):
    genesis_block = (0, int(time.time()), None, "0" * 64, 0)
    hasher = hashlib.sha256(str(genesis_block).encode('utf-8'))
    genesis_hash = hasher.hexdigest()
    cursor.execute(
        "INSERT INTO blockchain VALUES (0, %s, NULL, %s, 0, %s)",
        (genesis_block[1], genesis_block[3], genesis_hash)
    )
    print("-> Genesis Block created successfully.")

# -------------------- SETUP FUNCTION --------------------
def setup_database():
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()

        print("-> Deleting old database...")
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")

        print("-> Creating new database...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")

        print("-> Creating tables...")
        for desc in TABLES.values():
            cursor.execute(desc)

        print("-> Inserting data...")
        for name in ['users', 'restaurants', 'reviews', 'poll_tags']:
            cursor.execute(DATA[name])

        create_genesis_block(cursor)
        cnx.commit()
        cursor.close()
        cnx.close()

        print("\n✅✅✅ DATABASE SETUP COMPLETE! You can now run 'python server.py' ✅✅✅\n")

    except mysql.connector.Error as err:
        print(f"\n❌ DATABASE ERROR: {err}")
        print("❌ Please check your password and run this script again.\n")

# -------------------- ENTRY POINT --------------------
if __name__ == '__main__':
    setup_database()
