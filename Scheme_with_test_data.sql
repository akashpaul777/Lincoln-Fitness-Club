DROP DATABASE  IF  EXISTS `gym`; 
CREATE DATABASE  IF NOT EXISTS `gym`;
USE `gym`;


DROP TABLE IF EXISTS `Normalvisit`;
DROP TABLE IF EXISTS `Booking`;
DROP TABLE IF EXISTS `Payment`;
DROP TABLE IF EXISTS `Schedule`;
DROP TABLE IF EXISTS `Training`;
DROP TABLE IF EXISTS `News`;
DROP TABLE IF EXISTS `Staff`;
DROP TABLE IF EXISTS `Member`;
DROP TABLE IF EXISTS `MembershipTerm`;
DROP TABLE IF EXISTS `Price`;
CREATE TABLE `Price` (
  `PriceID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Value` decimal(8,2) NOT NULL,
  `IsMembershipTerm` tinyint(1) NOT NULL,
  PRIMARY KEY (`PriceID`)
);

INSERT INTO `Price` VALUES (1,'Yearly',500.00,1),(2,'Monthly',50.00,1),(3,'Special Training',20.00,0);


CREATE TABLE `MembershipTerm` (
  `MembershipTermID` int NOT NULL AUTO_INCREMENT,
  `Term` varchar(20) DEFAULT '1 year',
  `PriceID` int NOT NULL,
  PRIMARY KEY (`MembershipTermID`),
  FOREIGN KEY (`PriceID`) REFERENCES `Price` (`PriceID`)
); 

INSERT INTO `MembershipTerm` VALUES (123400,'Yearly',1),(123401,'Monthly',2);



CREATE TABLE `Member` (
  `MemberID` int NOT NULL AUTO_INCREMENT,
  `Firstname` varchar(45) DEFAULT NULL,
  `Lastname` varchar(45) DEFAULT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `DayOfBirth` date DEFAULT NULL,
  `Email` varchar(250) NOT NULL,
  `PhoneNumber` varchar(45) DEFAULT NULL,
  `HealthCondition` longtext,
  `HouseNumberName` varchar(15) DEFAULT NULL,
  `Street` varchar(45) DEFAULT NULL,
  `Town` varchar(25) DEFAULT NULL,
  `City` varchar(25) DEFAULT NULL,
  `Postalcode` varchar(4) DEFAULT NULL,
  `MembershipStartDate` date NOT NULL,
  `MembershipEndDate` date NOT NULL,
  `MembershipTerm` int NOT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT '1',
  `CardNumber` varchar(45) DEFAULT NULL,
  `CVV` varchar(5) DEFAULT NULL,
  `CardExpiry` varchar(10) DEFAULT NULL,
  `NameOnCard` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`MemberID`),
  FOREIGN KEY (`MembershipTerm`) REFERENCES `MembershipTerm` (`MembershipTermID`)
);


INSERT INTO `Member` VALUES (1001,'JensenBoss','Mcdonald','Male','1998-11-01','Jensen@gmail.com','0236541784','Good Health','88','Ellesmere Junction Road','Lincoln','Christchurch','7674','2023-03-01','2024-03-01',123400,1,'4242424242424242','342','2025-12','J Mcdonald'),(1002,'Taylor','Swift','Female','1989-12-13','Taylor@gmail.com','0212345678','Good Health','11','Ellesmere Junction Road','Lincoln','Christchurch','7674','2023-03-07','2023-04-07',123401,1,'4232323232323232','323','2025-12','T Swift'),(1003,'Kath','Brose','Female','1991-07-16','kath@gmail.com','0211144323','High Blood Pressure','88','Ellesmere Junction Road','Lincoln','Christchurch','7674','2022-03-16','2023-03-16',123400,0,'5555555555554444','123','2023-11','JensenBoss');


CREATE TABLE `Staff` (
  `StaffID` int NOT NULL AUTO_INCREMENT,
  `Firstname` varchar(45) DEFAULT NULL,
  `Lastname` varchar(45) DEFAULT NULL,
  `Gender` varchar(10) DEFAULT NULL,
  `DayOfBirth` date DEFAULT NULL,
  `Email` varchar(250) NOT NULL,
  `PhoneNumber` varchar(45) DEFAULT NULL,
  `HouseNumberName` varchar(15) DEFAULT NULL,
  `Street` varchar(45) DEFAULT NULL,
  `Town` varchar(25) DEFAULT NULL,
  `City` varchar(25) DEFAULT NULL,
  `Postalcode` varchar(4) DEFAULT NULL,
  `Introduction` longtext,
  `Position` varchar(45) DEFAULT NULL,
  `IsManager` tinyint(1) NOT NULL,
  `IsTrainer` tinyint(1) NOT NULL,
  `IsActive` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`StaffID`)
);
INSERT INTO `Staff` VALUES (2001,'Jose','Hedge','Male','1985-01-01','Jensen@gmail.com','0212341234','10','James Street','Lincoln','Christchurch','7608','I am a good trainer','Yoga Instructor',0,1,1),(2002,'San','Zhang','Male','1985-01-01','a@gmail.com','0212341234','11','James Street','Lincoln','Christchurch','7608','I am a good trainer','Yoga Instructor',0,1,1),(2003,'Si','Li','Male','1985-01-01','b@gmail.com','0212341234','12','James Street','Lincoln','Christchurch','7608','I am a good trainer','Yoga Instructor',0,1,1),(2004,'Wu','Wang','Male','1985-01-01','c@gmail.com','0212341234','13','James Street','Lincoln','Christchurch','7608','I am a good trainer','Yoga Instructor',0,1,1),(3001,'Cory','Shackelford','Female','1983-01-01','Cory@gmail.com','0222931234','07','James Street','Lincoln','Christchurch','7608','I am a good manager ;)','General Manager',1,0,1);







CREATE TABLE `News` (
  `NewsID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(150) NOT NULL,
  `Content` longtext NOT NULL,
  `UpdateDate` datetime NOT NULL,
  PRIMARY KEY (`NewsID`)
);

INSERT INTO `News` VALUES (123007,'Lift heavy or smaller weights ','So you want to lift weights but aren’t sure where to start. You scroll through your Instagram feed looking for guidance – but all you see are fitness influencers touting the idea you either lift big or don’t bother.\r\n\r\nThat’s a bit intimidating and disheartening, right? But as with most things exercise and health, its not really that simple.\r\n\r\nI’m an exercise scientist (and former Commonwealth powerlifting medallist and national Olympic weightlifting champion) who researches resistance training, also known as lifting weights. Research suggests lifting smaller weights and doing more repetitions (or, in gym parlance, “reps”) can have a role to play – but it all depends on your goals.\r\n\r\nIn short: if your goal is to build serious strength and bone density, lifting heavy is an efficient way to do it. But if you can’t lift heavy or it’s not your thing, please don’t think lifting lighter weights is a complete waste of time.','2023-03-27 20:05:27'),(123008,'HOW TO TRAIN FOR AN EVENT WHILE TEACHING','Love the idea of competing in an event but have no idea where to start? Four top athletes share tips on balancing training volume, recovery, and what to consider before you commit.','2023-03-27 20:06:37'),(123009,'8 WAYS TO LEARN CHOREOGRAPHY FASTER','We love receiving new releases, but learning them in a short space of time can be challenging. Here are 8 tips to help you get launch-ready!','2023-03-27 20:21:16'),(123010,'RAMADAN: HOW PRO TRAINERS GET THE BEST FROM FASTING','Observed by the majority of the 1.8 billion Muslims worldwide, Ramadan is a month of fasting, prayer, and reflection that offers many spiritual rewards – and some physical benefits too.\r\n\r\nEach year, Ramadan shifts according to the moon. In 2023 it starts on the evening of Wednesday, March 22 and ends at sundown on Thursday, April 20. During this period, Muslims fast between sunrise and sunset – eating only from iftar (the meal served after sunset) until suhoor (the meal served before dawn).','2023-03-27 20:24:55'),(123011,'INTERNATIONAL WOMEN’S DAY: #EMBRACE EQUITY','International Women’s Day 2023 encourages us to: “Imagine a gender equal world. A world free of bias, stereotypes, and discrimination. A world that\'s diverse, equitable, and inclusive.” Three women of Les Mills share how they #EmbraceEquity in their everyday lives.','2023-03-27 20:25:28'),(123012,'ARE YOU READY TO LEAD THE FUTURE OF FITNESS?','Did you know that Gen Z and Millennials – known collectively as ‘Generation Active’ for their love of workouts – now account for over 80% of the total fitness market? That means that if we want to keep packing out our classes for the long run, we need to ensure we’re providing a workout that attracts this generation into our studios.\r\n\r\nStrength training is back in a big way, with a recent MindBody report declaring it the most popular fitness genre of 2022. Again, Gen Z are driving this trend, wit','2023-03-27 20:25:54');



CREATE TABLE `Training` (
  `TrainingID` int NOT NULL AUTO_INCREMENT,
  `IsSpecializedTraining` tinyint(1) DEFAULT NULL,
  `IsClass` tinyint(1) DEFAULT NULL,
  `TrainingName` varchar(45) NOT NULL,
  `TrainingInfo` longtext NOT NULL,
  PRIMARY KEY (`TrainingID`)
);

INSERT INTO `Training` VALUES (1,1,0,'PT Intermediate Ievel 1','Lincoln Personal Trainers are fitness experts. Whatever your fitness goal — weight loss, strength gain, athletic performance, stress relief or simply motivation — a Les Mills Personal Trainer will work with you to achieve your goals and get results.'),(2,0,1,'SPRINT','SPRINT® is a 60-minute High-Intensity Interval Training (HIIT) workout, using an indoor bike to achieve fast results. It’s a short, intense style of training where the thrill and motivation comes from pushing your physical and mental limits. A high intensity, low impact workout, it\'s scientifically proven to return rapid results.'),(3,0,1,'BODYBALANCE','BODYBALANCE® is the yoga-based class that incorporates Tai Chi and Pilates.  During BODYBALANCE® an inspired soundtrack plays as you bend and stretch through a series of simple yoga moves and embrace elements of Tai Chi and Pilates. Breathing control is a part of all the exercises, and instructors will always provide options for those just getting started. You’ll strengthen your entire body and leave the class feeling calm and centered. '),(4,0,1,'BODYPUMP','BODYPUMP® is a barbell workout for anyone looking to get lean, toned and fit – fast.     Using light to moderate weights with lots of repetition, BODYPUMP® gives you a total body workout. Instructors will coach you through the scientifically proven moves and techniques pumping out encouragement, motivation and great music – helping you achieve much more than on your own! You’ll leave the class feeling challenged and motivated, ready to come back for more.'),(5,0,1,'GRIT Strength','GRIT Strength™ is a 30-minute high-intensity interval training (HIIT) workout, designed to improve strength, cardiovascular fitness and build lean muscle. This workout uses barbell, weight plate and bodyweight exercises to blast all major muscle groups. '),(6,0,1,'BODYATTACK','BODYATTACK® is a high-energy fitness class with moves that cater for total beginners to total addicts. We combine athletic movements like running, lunging and jumping with strength exercises such as push-ups and squats.'),(7,0,1,'THE TRIP','THE TRIP® is a fully immersive workout experience that combines a 40-minute multi-peak cycling workout with a journey through digitally-created worlds. With its cinema-scale screen and sound system, THE TRIP® takes motivation and energy output to the next level, burning serious calories.'),(8,0,1,'RPM','RPM® is the indoor cycling workout where you take on the terrain with your inspiring team coach who leads the pack through hills, flats, mountain peaks, time trials, and interval training.'),(9,1,0,'PT Starter','Lincoln Personal Trainers are fitness experts. Whatever your fitness goal — weight loss, strength gain, athletic performance, stress relief or simply motivation — a Les Mills Personal Trainer will work with you to achieve your goals and get results.'),(10,1,0,'PT Intermediate Ievel 2','Lincoln Personal Trainers are fitness experts. Whatever your fitness goal — weight loss, strength gain, athletic performance, stress relief or simply motivation — a Les Mills Personal Trainer will work with you to achieve your goals and get results.'),(11,1,0,'PT Professional','Lincoln Personal Trainers are fitness experts. Whatever your fitness goal — weight loss, strength gain, athletic performance, stress relief or simply motivation — a Les Mills Personal Trainer will work with you to achieve your goals and get results.');



CREATE TABLE `Schedule` (
  `ScheduleID` int NOT NULL AUTO_INCREMENT,
  `StaffID` int NOT NULL,
  `TrainingID` int DEFAULT NULL,
  `Room` varchar(25) NOT NULL,
  `PriceID` int DEFAULT NULL,
  `DurationInMinutes` time NOT NULL,
  `StartDate` date NOT NULL,
  `StartTime` time NOT NULL,
  `EndTime` time NOT NULL,
  `MaxCapacity` int NOT NULL,
  PRIMARY KEY (`ScheduleID`),
  FOREIGN KEY (`StaffID`) REFERENCES `Staff` (`StaffID`),
  FOREIGN KEY (`TrainingID`) REFERENCES `Training` (`TrainingID`),
  FOREIGN KEY (`PriceID`) REFERENCES `Price` (`PriceID`)
);



CREATE TABLE `Payment` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `Value` decimal(8,2) NOT NULL,
  `MemberID` int NOT NULL,
  `ScheduleID` int DEFAULT NULL,
  `PaymentDate` date NOT NULL,
  `PriceID` int DEFAULT NULL,
  PRIMARY KEY (`PaymentID`),
  FOREIGN KEY (`ScheduleID`) REFERENCES `Schedule` (`ScheduleID`),
  FOREIGN KEY (`MemberID`) REFERENCES `Member` (`MemberID`),
  FOREIGN KEY (`PriceID`) REFERENCES `Price` (`PriceID`)
);

INSERT INTO `Payment` VALUES (10000,500.00,1001,NULL,'2023-03-01',1),(10001,50.00,1002,NULL,'2023-03-07',2);



CREATE TABLE `Booking` (
  `BookingID` int NOT NULL AUTO_INCREMENT,
  `ScheduleID` int DEFAULT NULL,
  `MemberID` int NOT NULL,
  `IsAttended` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`BookingID`),
  FOREIGN KEY (`ScheduleID`) REFERENCES `Schedule` (`ScheduleID`),
  FOREIGN KEY (`MemberID`) REFERENCES `Member` (`MemberID`)
);



CREATE TABLE `Normalvisit` (
  `AttendID` int NOT NULL AUTO_INCREMENT,
  `MemberID` int NOT NULL,
  `AttendDate` date NOT NULL,
  PRIMARY KEY (`AttendID`),
  FOREIGN KEY (`MemberID`) REFERENCES `Member` (`MemberID`)
);


