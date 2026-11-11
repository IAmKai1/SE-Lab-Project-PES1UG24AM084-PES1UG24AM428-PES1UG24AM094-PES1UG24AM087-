"""
Extended demo catalog for LRG: well-known computer science titles across every subject,
so members can browse by subject and difficulty.

Each entry: (isbn, title, author, publisher, year, subject, difficulty).
Availability is assigned in database.py so roughly 40% of titles are checked out
and can take holds.
"""

AI_ML = "Artificial Intelligence & Machine Learning"
ALGO = "Algorithms & Data Structures"
ARCH = "Computer Architecture"
NET = "Computer Networks"
SEC = "Computer Security"
DB = "Databases & Data Systems"
MATH = "Mathematics for Computing"
OS = "Operating Systems"
PL = "Programming Languages"
DESIGN = "Software Design & Architecture"
SE = "Software Engineering"
TEST = "Software Testing"
THEORY = "Theory of Computation & Compilers"

EXTENDED_TITLES = [
    # Artificial Intelligence & Machine Learning
    ("978-0134610993", "Artificial Intelligence: A Modern Approach (4th Ed.)", "Stuart Russell, Peter Norvig", "Pearson", 2020, AI_ML, "Intermediate"),
    ("978-0262035613", "Deep Learning", "Ian Goodfellow, Yoshua Bengio, Aaron Courville", "MIT Press", 2016, AI_ML, "Advanced"),
    ("978-0387310732", "Pattern Recognition and Machine Learning", "Christopher M. Bishop", "Springer", 2006, AI_ML, "Advanced"),
    ("978-1098125974", "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow (3rd Ed.)", "Aurélien Géron", "O'Reilly Media", 2022, AI_ML, "Beginner"),
    ("978-0070428072", "Machine Learning", "Tom M. Mitchell", "McGraw-Hill", 1997, AI_ML, "Intermediate"),
    ("978-0387848570", "The Elements of Statistical Learning (2nd Ed.)", "Trevor Hastie, Robert Tibshirani, Jerome Friedman", "Springer", 2009, AI_ML, "Advanced"),
    ("978-0262039246", "Reinforcement Learning: An Introduction (2nd Ed.)", "Richard S. Sutton, Andrew G. Barto", "MIT Press", 2018, AI_ML, "Advanced"),
    ("978-1461471370", "An Introduction to Statistical Learning", "Gareth James, Daniela Witten, Trevor Hastie, Robert Tibshirani", "Springer", 2013, AI_ML, "Beginner"),
    ("978-1617296864", "Deep Learning with Python (2nd Ed.)", "François Chollet", "Manning", 2021, AI_ML, "Beginner"),
    ("978-0262018029", "Machine Learning: A Probabilistic Perspective", "Kevin P. Murphy", "MIT Press", 2012, AI_ML, "Advanced"),
    ("978-0131873216", "Speech and Language Processing (2nd Ed.)", "Daniel Jurafsky, James H. Martin", "Pearson", 2008, AI_ML, "Advanced"),

    # Algorithms & Data Structures
    ("978-0321573513", "Algorithms (4th Ed.)", "Robert Sedgewick, Kevin Wayne", "Addison-Wesley", 2011, ALGO, "Intermediate"),
    ("978-0321295354", "Algorithm Design", "Jon Kleinberg, Éva Tardos", "Pearson", 2005, ALGO, "Advanced"),
    ("978-1848000698", "The Algorithm Design Manual (2nd Ed.)", "Steven S. Skiena", "Springer", 2008, ALGO, "Intermediate"),
    ("978-1617292231", "Grokking Algorithms", "Aditya Bhargava", "Manning", 2016, ALGO, "Beginner"),
    ("978-0984782857", "Cracking the Coding Interview (6th Ed.)", "Gayle Laakmann McDowell", "CareerCup", 2015, ALGO, "Beginner"),
    ("978-0201657883", "Programming Pearls (2nd Ed.)", "Jon Bentley", "Addison-Wesley", 1999, ALGO, "Intermediate"),
    ("978-0073523408", "Algorithms", "Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani", "McGraw-Hill", 2006, ALGO, "Intermediate"),
    ("978-0132576277", "Data Structures and Algorithm Analysis in Java (3rd Ed.)", "Mark Allen Weiss", "Pearson", 2011, ALGO, "Intermediate"),

    # Computer Architecture
    ("978-0124077263", "Computer Organization and Design: The Hardware/Software Interface (5th Ed.)", "David A. Patterson, John L. Hennessy", "Morgan Kaufmann", 2013, ARCH, "Intermediate"),
    ("978-0128119051", "Computer Architecture: A Quantitative Approach (6th Ed.)", "John L. Hennessy, David A. Patterson", "Morgan Kaufmann", 2017, ARCH, "Advanced"),
    ("978-0134092669", "Computer Systems: A Programmer's Perspective (3rd Ed.)", "Randal E. Bryant, David R. O'Hallaron", "Pearson", 2015, ARCH, "Intermediate"),
    ("978-0262640688", "The Elements of Computing Systems", "Noam Nisan, Shimon Schocken", "MIT Press", 2005, ARCH, "Beginner"),
    ("978-0735611313", "Code: The Hidden Language of Computer Hardware and Software", "Charles Petzold", "Microsoft Press", 2000, ARCH, "Beginner"),
    ("978-0123944245", "Digital Design and Computer Architecture (2nd Ed.)", "David Money Harris, Sarah L. Harris", "Morgan Kaufmann", 2012, ARCH, "Intermediate"),
    ("978-0132916523", "Structured Computer Organization (6th Ed.)", "Andrew S. Tanenbaum, Todd Austin", "Pearson", 2012, ARCH, "Intermediate"),

    # Computer Networks
    ("978-0133594140", "Computer Networking: A Top-Down Approach (7th Ed.)", "James F. Kurose, Keith W. Ross", "Pearson", 2016, NET, "Intermediate"),
    ("978-0132126953", "Computer Networks (5th Ed.)", "Andrew S. Tanenbaum, David J. Wetherall", "Pearson", 2010, NET, "Intermediate"),
    ("978-0123850591", "Computer Networks: A Systems Approach (5th Ed.)", "Larry L. Peterson, Bruce S. Davie", "Morgan Kaufmann", 2011, NET, "Intermediate"),
    ("978-0321336316", "TCP/IP Illustrated, Vol. 1: The Protocols (2nd Ed.)", "Kevin R. Fall, W. Richard Stevens", "Addison-Wesley", 2011, NET, "Advanced"),
    ("978-0131411555", "UNIX Network Programming, Vol. 1 (3rd Ed.)", "W. Richard Stevens, Bill Fenner, Andrew M. Rudoff", "Addison-Wesley", 2003, NET, "Advanced"),
    ("978-1449344764", "High Performance Browser Networking", "Ilya Grigorik", "O'Reilly Media", 2013, NET, "Intermediate"),
    ("978-0073250328", "Data Communications and Networking (4th Ed.)", "Behrouz A. Forouzan", "McGraw-Hill", 2007, NET, "Beginner"),

    # Computer Security
    ("978-0470068526", "Security Engineering (2nd Ed.)", "Ross Anderson", "Wiley", 2008, SEC, "Advanced"),
    ("978-1118026472", "The Web Application Hacker's Handbook (2nd Ed.)", "Dafydd Stuttard, Marcus Pinto", "Wiley", 2011, SEC, "Intermediate"),
    ("978-1119096726", "Applied Cryptography (20th Anniv. Ed.)", "Bruce Schneier", "Wiley", 2015, SEC, "Advanced"),
    ("978-1593278267", "Serious Cryptography", "Jean-Philippe Aumasson", "No Starch Press", 2017, SEC, "Intermediate"),
    ("978-1593271442", "Hacking: The Art of Exploitation (2nd Ed.)", "Jon Erickson", "No Starch Press", 2008, SEC, "Advanced"),
    ("978-0134794105", "Computer Security: Principles and Practice (4th Ed.)", "William Stallings, Lawrie Brown", "Pearson", 2017, SEC, "Intermediate"),
    ("978-0133354690", "Cryptography and Network Security (6th Ed.)", "William Stallings", "Pearson", 2013, SEC, "Intermediate"),
    ("978-0764542800", "The Art of Deception", "Kevin D. Mitnick, William L. Simon", "Wiley", 2002, SEC, "Beginner"),

    # Databases & Data Systems
    ("978-0078022159", "Database System Concepts (7th Ed.)", "Abraham Silberschatz, Henry F. Korth, S. Sudarshan", "McGraw-Hill", 2019, DB, "Intermediate"),
    ("978-0133970777", "Fundamentals of Database Systems (7th Ed.)", "Ramez Elmasri, Shamkant B. Navathe", "Pearson", 2015, DB, "Intermediate"),
    ("978-0072465631", "Database Management Systems (3rd Ed.)", "Raghu Ramakrishnan, Johannes Gehrke", "McGraw-Hill", 2002, DB, "Intermediate"),
    ("978-1492057611", "Learning SQL (3rd Ed.)", "Alan Beaulieu", "O'Reilly Media", 2020, DB, "Beginner"),
    ("978-1934356555", "SQL Antipatterns", "Bill Karwin", "Pragmatic Bookshelf", 2010, DB, "Intermediate"),
    ("978-1492040347", "Database Internals", "Alex Petrov", "O'Reilly Media", 2019, DB, "Advanced"),
    ("978-1934356920", "Seven Databases in Seven Weeks", "Eric Redmond, Jim R. Wilson", "Pragmatic Bookshelf", 2012, DB, "Intermediate"),

    # Mathematics for Computing
    ("978-0073383095", "Discrete Mathematics and Its Applications (7th Ed.)", "Kenneth H. Rosen", "McGraw-Hill", 2011, MATH, "Beginner"),
    ("978-0201558029", "Concrete Mathematics (2nd Ed.)", "Ronald L. Graham, Donald E. Knuth, Oren Patashnik", "Addison-Wesley", 1994, MATH, "Advanced"),
    ("978-0980232776", "Introduction to Linear Algebra (5th Ed.)", "Gilbert Strang", "Wellesley-Cambridge Press", 2016, MATH, "Intermediate"),
    ("978-3319110790", "Linear Algebra Done Right (3rd Ed.)", "Sheldon Axler", "Springer", 2015, MATH, "Advanced"),
    ("978-1108455145", "Mathematics for Machine Learning", "Marc Peter Deisenroth, A. Aldo Faisal, Cheng Soon Ong", "Cambridge University Press", 2020, MATH, "Intermediate"),
    ("978-0387402727", "All of Statistics", "Larry Wasserman", "Springer", 2004, MATH, "Advanced"),
    ("978-0521675994", "How to Prove It (2nd Ed.)", "Daniel J. Velleman", "Cambridge University Press", 2006, MATH, "Beginner"),

    # Operating Systems
    ("978-1118063330", "Operating System Concepts (9th Ed.)", "Abraham Silberschatz, Peter B. Galvin, Greg Gagne", "Wiley", 2012, OS, "Intermediate"),
    ("978-0133591620", "Modern Operating Systems (4th Ed.)", "Andrew S. Tanenbaum, Herbert Bos", "Pearson", 2014, OS, "Intermediate"),
    ("978-1985086593", "Operating Systems: Three Easy Pieces", "Remzi H. Arpaci-Dusseau, Andrea C. Arpaci-Dusseau", "CreateSpace", 2018, OS, "Beginner"),
    ("978-0134670959", "Operating Systems: Internals and Design Principles (9th Ed.)", "William Stallings", "Pearson", 2017, OS, "Intermediate"),
    ("978-1593272203", "The Linux Programming Interface", "Michael Kerrisk", "No Starch Press", 2010, OS, "Advanced"),
    ("978-0321637734", "Advanced Programming in the UNIX Environment (3rd Ed.)", "W. Richard Stevens, Stephen A. Rago", "Addison-Wesley", 2013, OS, "Advanced"),
    ("978-0596005658", "Understanding the Linux Kernel (3rd Ed.)", "Daniel P. Bovet, Marco Cesati", "O'Reilly Media", 2005, OS, "Advanced"),
    ("978-0672329463", "Linux Kernel Development (3rd Ed.)", "Robert Love", "Addison-Wesley", 2010, OS, "Advanced"),

    # Programming Languages
    ("978-1593279288", "Python Crash Course (2nd Ed.)", "Eric Matthes", "No Starch Press", 2019, PL, "Beginner"),
    ("978-1492056355", "Fluent Python (2nd Ed.)", "Luciano Ramalho", "O'Reilly Media", 2022, PL, "Intermediate"),
    ("978-0134685991", "Effective Java (3rd Ed.)", "Joshua Bloch", "Addison-Wesley", 2018, PL, "Intermediate"),
    ("978-0262510875", "Structure and Interpretation of Computer Programs (2nd Ed.)", "Harold Abelson, Gerald Jay Sussman", "MIT Press", 1996, PL, "Intermediate"),
    ("978-0321563842", "The C++ Programming Language (4th Ed.)", "Bjarne Stroustrup", "Addison-Wesley", 2013, PL, "Advanced"),
    ("978-1718500440", "The Rust Programming Language", "Steve Klabnik, Carol Nichols", "No Starch Press", 2019, PL, "Intermediate"),
    ("978-0134190440", "The Go Programming Language", "Alan A. A. Donovan, Brian W. Kernighan", "Addison-Wesley", 2015, PL, "Intermediate"),
    ("978-1593279509", "Eloquent JavaScript (3rd Ed.)", "Marijn Haverbeke", "No Starch Press", 2018, PL, "Beginner"),
    ("978-0321334879", "Effective C++ (3rd Ed.)", "Scott Meyers", "Addison-Wesley", 2005, PL, "Advanced"),
    ("978-0596009205", "Head First Java (2nd Ed.)", "Kathy Sierra, Bert Bates", "O'Reilly Media", 2005, PL, "Beginner"),

    # Software Design & Architecture
    ("978-0321127426", "Patterns of Enterprise Application Architecture", "Martin Fowler", "Addison-Wesley", 2002, DESIGN, "Advanced"),
    ("978-0321815736", "Software Architecture in Practice (3rd Ed.)", "Len Bass, Paul Clements, Rick Kazman", "Addison-Wesley", 2012, DESIGN, "Advanced"),
    ("978-1492043454", "Fundamentals of Software Architecture", "Mark Richards, Neal Ford", "O'Reilly Media", 2020, DESIGN, "Intermediate"),
    ("978-0321200686", "Enterprise Integration Patterns", "Gregor Hohpe, Bobby Woolf", "Addison-Wesley", 2003, DESIGN, "Advanced"),
    ("978-1732102200", "A Philosophy of Software Design", "John Ousterhout", "Yaknyam Press", 2018, DESIGN, "Beginner"),
    ("978-1617294549", "Microservices Patterns", "Chris Richardson", "Manning", 2018, DESIGN, "Advanced"),

    # Software Engineering
    ("978-0201835953", "The Mythical Man-Month (Anniv. Ed.)", "Frederick P. Brooks Jr.", "Addison-Wesley", 1995, SE, "Beginner"),
    ("978-0073375977", "Software Engineering: A Practitioner's Approach (7th Ed.)", "Roger S. Pressman", "McGraw-Hill", 2009, SE, "Intermediate"),
    ("978-0133943030", "Software Engineering (10th Ed.)", "Ian Sommerville", "Pearson", 2015, SE, "Intermediate"),
    ("978-0735619678", "Code Complete (2nd Ed.)", "Steve McConnell", "Microsoft Press", 2004, SE, "Intermediate"),
    # (Refactoring, 978-0134757599, is left out: the admin tests add it as a new catalog entry.)
    ("978-0321934116", "Peopleware: Productive Projects and Teams (3rd Ed.)", "Tom DeMarco, Timothy Lister", "Addison-Wesley", 2013, SE, "Beginner"),
    ("978-0137081073", "The Clean Coder", "Robert C. Martin", "Prentice Hall", 2011, SE, "Beginner"),
    ("978-0131177055", "Working Effectively with Legacy Code", "Michael Feathers", "Prentice Hall", 2004, SE, "Advanced"),
    ("978-0321601919", "Continuous Delivery", "Jez Humble, David Farley", "Addison-Wesley", 2010, SE, "Intermediate"),
    ("978-1942788294", "The Phoenix Project (5th Anniv. Ed.)", "Gene Kim, Kevin Behr, George Spafford", "IT Revolution Press", 2018, SE, "Beginner"),
    ("978-1942788331", "Accelerate", "Nicole Forsgren, Jez Humble, Gene Kim", "IT Revolution Press", 2018, SE, "Beginner"),
    ("978-0321278654", "Extreme Programming Explained (2nd Ed.)", "Kent Beck, Cynthia Andres", "Addison-Wesley", 2004, SE, "Beginner"),

    # Software Testing
    ("978-1118031964", "The Art of Software Testing (3rd Ed.)", "Glenford J. Myers, Corey Sandler, Tom Badgett", "Wiley", 2011, TEST, "Beginner"),
    ("978-0321534460", "Agile Testing", "Lisa Crispin, Janet Gregory", "Addison-Wesley", 2009, TEST, "Intermediate"),
    ("978-0131495050", "xUnit Test Patterns", "Gerard Meszaros", "Addison-Wesley", 2007, TEST, "Advanced"),
    ("978-1617290893", "The Art of Unit Testing (2nd Ed.)", "Roy Osherove", "Manning", 2013, TEST, "Beginner"),
    ("978-1617296277", "Unit Testing Principles, Practices, and Patterns", "Vladimir Khorikov", "Manning", 2020, TEST, "Intermediate"),
    ("978-0521880381", "Introduction to Software Testing", "Paul Ammann, Jeff Offutt", "Cambridge University Press", 2008, TEST, "Intermediate"),
    ("978-1680502404", "Python Testing with pytest", "Brian Okken", "Pragmatic Bookshelf", 2017, TEST, "Beginner"),
    ("978-0471081128", "Lessons Learned in Software Testing", "Cem Kaner, James Bach, Bret Pettichord", "Wiley", 2002, TEST, "Intermediate"),

    # Theory of Computation & Compilers
    ("978-1133187790", "Introduction to the Theory of Computation (3rd Ed.)", "Michael Sipser", "Cengage Learning", 2012, THEORY, "Advanced"),
    ("978-0321455369", "Introduction to Automata Theory, Languages, and Computation (3rd Ed.)", "John E. Hopcroft, Rajeev Motwani, Jeffrey D. Ullman", "Pearson", 2006, THEORY, "Advanced"),
    ("978-0321486813", "Compilers: Principles, Techniques, and Tools (2nd Ed.)", "Alfred V. Aho, Monica S. Lam, Ravi Sethi, Jeffrey D. Ullman", "Pearson", 2006, THEORY, "Advanced"),
    ("978-0465026562", "Gödel, Escher, Bach: An Eternal Golden Braid", "Douglas R. Hofstadter", "Basic Books", 1999, THEORY, "Intermediate"),
    ("978-1284077247", "An Introduction to Formal Languages and Automata (6th Ed.)", "Peter Linz", "Jones & Bartlett Learning", 2016, THEORY, "Intermediate"),
    ("978-0990582939", "Crafting Interpreters", "Robert Nystrom", "Genever Benning", 2021, THEORY, "Intermediate"),
    ("978-0120884780", "Engineering a Compiler (2nd Ed.)", "Keith D. Cooper, Linda Torczon", "Morgan Kaufmann", 2011, THEORY, "Advanced"),
]
