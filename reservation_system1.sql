-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 10, 2019 at 03:58 PM
-- Server version: 10.4.6-MariaDB
-- PHP Version: 7.1.32

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `reservation_system1`
--

-- --------------------------------------------------------

--
-- Table structure for table `airline`
--

CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('China Eastern');

-- --------------------------------------------------------

--
-- Table structure for table `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
('admin', 'e2fc714c4727ee9395f324cd2e7f331f', 'Roe', 'Zhang', '1978-05-25', 'China Eastern');

-- --------------------------------------------------------

--
-- Table structure for table `airplane`
--

CREATE TABLE `airplane` (
  `airline_name` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  `seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airplane`
--

INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
('China Eastern', 1, 4),
('China Eastern', 2, 4),
('China Eastern', 3, 50);

-- --------------------------------------------------------

--
-- Table structure for table `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(50) NOT NULL,
  `airport_city` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `airport`
--

INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
('BEI', 'Beijing'),
('BOS', 'Boston'),
('HKA', 'Hong Kong'),
('JFK', 'NYC'),
('LAX', 'Los Angles'),
('PVG', 'Shanghai'),
('SFO', 'San Francisco'),
('SHEN', 'Shenzhen');

-- --------------------------------------------------------

--
-- Table structure for table `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `booking_agent_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES
('ctrip@agent.com', 'e19d5cd5af0378da05f63f891c7467af', 1),
('expedia@agent.com', 'e19d5cd5af0378da05f63f891c7467af', 2);

-- --------------------------------------------------------

--
-- Table structure for table `customer`
--

CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `building_number` varchar(30) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` varchar(50) DEFAULT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('testcustomer@nyu.edu', 'Test Customer 1', '81dc9bdb52d04dc20036dbd8313ed055', '1555', 'Century Avenue', 'Pudong', 'Shanghai', '123-4321-4321', '54321', '2025-12-24', 'China', '1999-12-19'),
('user1@nyu.edu', 'User 1', '81dc9bdb52d04dc20036dbd8313ed055', '1555', 'Century Avenue', 'Pudong', 'Shanghai', '123-4321-4322', '54322', '2025-12-25', 'China', '1999-11-19'),
('user2@nyu.edu', 'User 2', '81dc9bdb52d04dc20036dbd8313ed055', '1702', 'Century Avenue', 'Pudong', 'Shanghai', '123-4323-4323', '54323', '2025-10-24', 'China', '1999-10-19'),
('user3@nyu.edu', 'User 3', '81dc9bdb52d04dc20036dbd8313ed055', '1890', 'Century Avenue', 'Pudong', 'Shanghai', '123-4324-4324', '54324', '2025-09-24', 'China', '1999-09-19');

-- --------------------------------------------------------

--
-- Table structure for table `flight`
--

CREATE TABLE `flight` (
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(50) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(50) NOT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `status` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`) VALUES
('China Eastern', 102, 'SFO', '2019-11-12 13:25:25', 'LAX', '2019-11-12 16:50:25', '300', 'on-time', 3),
('China Eastern', 104, 'PVG', '2019-12-12 13:25:25', 'BEI', '2019-12-12 16:50:25', '300', 'on-time', 3),
('China Eastern', 106, 'SFO', '2019-10-12 13:25:25', 'LAX', '2019-10-12 16:50:25', '350', 'delayed', 3),
('China Eastern', 134, 'JFK', '2019-08-12 13:25:25', 'BOS', '2019-08-12 16:50:25', '300', 'delayed', 3),
('China Eastern', 206, 'SFO', '2020-01-12 13:25:25', 'LAX', '2020-01-12 16:50:25', '400', 'on-time', 2),
('China Eastern', 207, 'LAX', '2020-02-12 13:25:25', 'SFO', '2020-02-12 16:50:25', '300', 'on-time', 2),
('China Eastern', 296, 'PVG', '2020-01-01 13:25:25', 'SFO', '2020-01-01 16:50:25', '3000', 'on-time', 1),
('China Eastern', 715, 'PVG', '2019-11-28 10:25:25', 'BEI', '2019-11-28 13:50:25', '500', 'delayed', 1),
('China Eastern', 839, 'SHEN', '2019-02-12 13:25:25', 'BEI', '2019-02-12 16:50:25', '300', 'on-time', 1);

-- --------------------------------------------------------

--
-- Table structure for table `phone`
--

CREATE TABLE `phone` (
  `username` varchar(50) NOT NULL,
  `phone_num` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `phone`
--

INSERT INTO `phone` (`username`, `phone_num`) VALUES
('admin', '111-2222-3333'),
('admin', '444-5555-6666');

-- --------------------------------------------------------

--
-- Table structure for table `purchases`
--

CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(50) NOT NULL,
  `agent_email` varchar(50) DEFAULT NULL,
  `card_type` varchar(20) NOT NULL,
  `card_num` varchar(50) DEFAULT NULL,
  `name_on_card` varchar(50) NOT NULL,
  `purchase_datetime` datetime NOT NULL,
  `card_exp_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `purchases`
--

INSERT INTO `purchases` (`ticket_id`, `customer_email`, `agent_email`, `card_type`, `card_num`, `name_on_card`, `purchase_datetime`, `card_exp_date`) VALUES
(1, 'testcustomer@nyu.edu', 'ctrip@agent.com', 'credit', '1111-2222-3333-4444', 'Test Customer 1', '2019-10-12 11:55:55', '2023-03-01'),
(2, 'user1@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'User 1', '2019-10-11 11:55:55', '2023-03-01'),
(3, 'user2@nyu.edu', NULL, '', '1111-2222-3333-5555', 'User 2', '2019-11-11 11:55:55', '2023-03-01'),
(4, 'user1@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'Test Customer 1', '2019-10-21 11:55:55', '2023-03-01'),
(5, 'testcustomer@nyu.edu', 'ctrip@agent.com', 'credit', ' 1111-2222-3333-4444', 'Test Customer 1', '2019-11-28 11:55:55', '2023-03-01'),
(6, 'testcustomer@nyu.edu', 'ctrip@agent.com', 'credit', '1111-2222-3333-4444', 'Test Customer 1', '2019-10-05 11:55:55', '2023-03-01'),
(7, 'user3@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'User 3', '2019-09-03 11:55:55', '2023-03-01'),
(8, 'user3@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'User 3', '2019-02-03 11:55:55', '2023-03-01'),
(9, 'user3@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'User 3', '2019-09-03 11:55:55', '2023-03-01'),
(11, 'user3@nyu.edu', 'expedia@agent.com', 'credit', '1111-2222-3333-5555', 'User 3', '2019-02-23 11:55:55', '2023-03-01'),
(12, 'testcustomer@nyu.edu', 'ctrip@agent.com', 'credit', '1111-2222-3333-4444', 'Test Customer 1', '2019-10-05 11:55:55', '2023-03-01'),
(14, 'user3@nyu.edu', 'ctrip@agent.com', 'credit', '1111-2222-3333-5555', 'User 3', '2019-12-05 11:55:55', '2023-03-01'),
(15, 'user1@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'User 1', '2019-12-06 11:55:55', '2023-03-01'),
(16, 'user2@nyu.edu', NULL, 'credit', '1111-2222-3333-5555', 'User 2', '2019-11-19 11:55:55', '2023-03-01'),
(17, 'user1@nyu.edu', 'ctrip@agent.com', 'credit', '1111-2222-3333-5555', 'User 1', '2019-10-11 11:55:55', '2023-03-01'),
(18, 'testcustomer@nyu.edu', 'ctrip@agent.com', 'credit', '1111-2222-3333-4444', 'Test Customer 1', '2019-11-25 11:55:55', '2023-03-01'),
(19, 'user1@nyu.edu', 'expedia@agent.com', 'credit', '1111-2222-3333-5555', 'User 1', '2019-12-04 11:55:55', '2023-03-01'),
(20, 'testcustomer@nyu.edu', NULL, 'credit', '1111-2222-3333-4444', 'Test Customer 1', '2019-09-12 11:55:55', '2023-03-01');

-- --------------------------------------------------------

--
-- Table structure for table `review`
--

CREATE TABLE `review` (
  `email` varchar(50) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `comments` varchar(300) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `review`
--

INSERT INTO `review` (`email`, `airline_name`, `flight_num`, `rating`, `comments`) VALUES
('testcustomer@nyu.edu', 'China Eastern', 102, 4, 'Very Comfortable'),
('testcustomer@nyu.edu', 'China Eastern', 104, 1, 'Customer Care services are not\r\ngood'),
('user1@nyu.edu', 'China Eastern', 102, 5, 'Relaxing, check-in and onboarding very\r\nprofessional'),
('user1@nyu.edu', 'China Eastern', 104, 5, 'Comfortable journey and Professional'),
('user2@nyu.edu', 'China Eastern', 102, 3, 'Satisfied and will use the same flight again');

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `sold_price` decimal(10,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`, `sold_price`) VALUES
(1, 'China Eastern', 102, '300'),
(2, 'China Eastern', 102, '300'),
(3, 'China Eastern', 102, '300'),
(4, 'China Eastern', 104, '300'),
(5, 'China Eastern', 104, '300'),
(6, 'China Eastern', 106, '350'),
(7, 'China Eastern', 106, '350'),
(8, 'China Eastern', 839, '300'),
(9, 'China Eastern', 102, '360'),
(11, 'China Eastern', 134, '300'),
(12, 'China Eastern', 715, '500'),
(14, 'China Eastern', 206, '400'),
(15, 'China Eastern', 206, '400'),
(16, 'China Eastern', 206, '400'),
(17, 'China Eastern', 207, '300'),
(18, 'China Eastern', 207, '300'),
(19, 'China Eastern', 296, '3000'),
(20, 'China Eastern', 296, '3000');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`airline_name`);

--
-- Indexes for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`),
  ADD KEY `username` (`username`);

--
-- Indexes for table `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`airline_name`,`airplane_id`);

--
-- Indexes for table `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`airport_name`);

--
-- Indexes for table `booking_agent`
--
ALTER TABLE `booking_agent`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- Indexes for table `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`airline_name`,`flight_num`),
  ADD KEY `airline_name` (`airline_name`,`airplane_id`),
  ADD KEY `departure_airport` (`departure_airport`),
  ADD KEY `arrival_airport` (`arrival_airport`);

--
-- Indexes for table `phone`
--
ALTER TABLE `phone`
  ADD PRIMARY KEY (`username`,`phone_num`),
  ADD KEY `username` (`username`);

--
-- Indexes for table `purchases`
--
ALTER TABLE `purchases`
  ADD PRIMARY KEY (`ticket_id`,`customer_email`),
  ADD KEY `agent_email` (`agent_email`),
  ADD KEY `customer_email` (`customer_email`);

--
-- Indexes for table `review`
--
ALTER TABLE `review`
  ADD PRIMARY KEY (`email`,`airline_name`,`flight_num`),
  ADD KEY `airline_name` (`airline_name`,`flight_num`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `airline_name` (`airline_name`,`flight_num`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- Constraints for table `airplane`
--
ALTER TABLE `airplane`
  ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- Constraints for table `flight`
--
ALTER TABLE `flight`
  ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`airline_name`,`airplane_id`) REFERENCES `airplane` (`airline_name`, `airplane_id`),
  ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`departure_airport`) REFERENCES `airport` (`airport_name`),
  ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`arrival_airport`) REFERENCES `airport` (`airport_name`);

--
-- Constraints for table `phone`
--
ALTER TABLE `phone`
  ADD CONSTRAINT `phone_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`);

--
-- Constraints for table `purchases`
--
ALTER TABLE `purchases`
  ADD CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`),
  ADD CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`agent_email`) REFERENCES `booking_agent` (`email`),
  ADD CONSTRAINT `purchases_ibfk_3` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`);

--
-- Constraints for table `review`
--
ALTER TABLE `review`
  ADD CONSTRAINT `review_ibfk_1` FOREIGN KEY (`email`) REFERENCES `customer` (`email`),
  ADD CONSTRAINT `review_ibfk_2` FOREIGN KEY (`airline_name`,`flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`);

--
-- Constraints for table `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`airline_name`,`flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
