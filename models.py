class User:
    id = None
    firstname = None
    lastname = None
    dayOfBirth = None
    email = None
    phoneNumber = None
    isManager = False
    isMember = False
    isTrainer = False
    def setData(self, userData):
        if "IsManager" in userData:
            self.id = userData['StaffID']
            self.isManager = bool(userData['IsManager'])
        if "IsTrainer" in userData:    
            self.id = userData['StaffID']
            self.isTrainer = bool(userData['IsTrainer'])
        else:
            self.id = userData['MemberID']
            self.isMember = 1
            self.membershipEndDate = userData['MembershipEndDate']
        self.firstname = userData['Firstname']
        self.lastname = userData['Lastname']
        self.dayOfBirth = userData['DayOfBirth']
        self.email = userData['Email']
        self.phoneNumber = userData['PhoneNumber']
        self.isActive = userData['IsActive']
