from dataclasses import dataclass


@dataclass
class Story:
    name: str
    pov_info: str

    def __init__(
            self, name: str, 
            pov_info: str = None
        ):
        self.name = name
        if pov_info:
            self.pov_info = f"The story is in first person perspective. The narrator's name is {pov_info}."
        else:
            self.pov_info = "The story is in third person perspective."


story_info_list = [
    Story(
        name="A Drop Of Haunted Blood"
    ),
    Story(
        name="A Hero of Our Time",
        pov_info="The traveller"
    ),
    # Story(
    #     name="A Room With A View"
    # ),
    # Story(
    #     name="Alice's Adventures in Wonderland"
    # ),
    # Story(
    #     name="Apex",
    #     pov_info="Allix"
    # ),
    # Story(
    #     name="Around the World in 80 Days"
    # ),
    # Story(
    #     name="Bleak House"
    # ),
    # Story(
    #     name="BREAKING SHADOWS (Shadows Book 1)",
    #     pov_info="Riley Archer"
    # ),
    # Story(
    #     name="Checkmate",
    #     pov_info="Rose"
    # ),
    # Story(
    #     name="Down World (Book 1 of the Down World Series)",
    #     pov_info="Marina"
    # ),
    # Story(
    #     name="Dr. Jekyll and Mr. Hyde"
    # ),
    # Story(
    #     name="Find a Penny, Pick Her Up",
    #     pov_info="Penny"
    # ),
    # Story(
    #     name="Frankenstein",
    #     pov_info="Robert Walton"
    # ),
    # Story(
    #     name="From the Earth to the Moon"
    # ),
    # Story(
    #     name="Grapes of Wrath"
    # ),
    # Story(
    #     name = "Horus",
    #     pov_info = "Amar"
    # ),
    # Story(
    #     name="Human Code",
    #     pov_info="Javier Morales"
    # ),
    # Story(
    #     name="KING SOLOMON'S MINES",
    #     pov_info="Allan Quatermain"
    # ),
    # Story(
    #     name="Mask of Celibacy",
    #     pov_info="Jess"
    # ),
    # Story(
    #     name="Middlemarch"
    # ),
    # Story(
    #     name="Persuasion"
    # ),
    # Story(
    #     name="Peter Pan",
    #     pov_info="The Narrator"
    # ),
    # Story(
    #     name="Priestess of The Moon",
    #     pov_info="Li Xiang"
    # ),
    # Story(
    #     name="Prospect: Paradigm"
    # ),
    # Story(
    #     name="Quill of Thieves"
    # ),
    # Story(
    #     name="Red_Rover",
    #     pov_info="Meg"
    # ),
    # Story(
    #     name="Road to Arcadia"
    # ),
    # Story(
    #     name="Sherlock_Holmes_and_The_Hound_of_Baskervilles",
    #     pov_info="Dr. Watson"
    # ),
    # Story(
    #     name="Situationship [Complete]",
    #     pov_info="Heath"
    # ),
    # Story(
    #     name="Tattered Paige | Book 1",
    #     pov_info="Ima Jean Paige"
    # ),
    # Story(
    #     name="The Adventures of Huckleberry Finn",
    #     pov_info="Huckleberry Finn"
    # ),
    # Story(
    #     name="The Deerslayer"
    # ),
    # Story(
    #     name="The God Codex",
    #     pov_info="Mia Love"
    # ),
    # Story(
    #     name="The Hunt for Power"
    # ),
    # Story(
    #     name="The Invisible Man"
    # ),
    # Story(
    #     name="The Key to Anchor Lake ✓",
    #     pov_info="Blaire Bloxham"
    # ),
    # Story(
    #     name="The Last Scarecrow"
    # ),
    # Story(
    #     name="The Marvels"
    # ),
    # Story(
    #     name="The Palmer Pool", 
    #     pov_info="Vanessa Brooks"
    # ),
    # Story(
    #     name="The Picture of Dorian Gray"
    # ),
    # Story(
    #     name="The Plague Doctor's Daughter"
    # ),
    # Story(
    #     name="the sable spy"
    # ),
    # Story(
    #     name="The Secret Garden"
    # ),
    # Story(
    #     name="The Time Machine",
    #     pov_info="The Time Traveller"
    # ),
    # Story(
    #     name="THE WIND IN THE WILLOWS"
    # ),
    # Story(
    #     name="True (Male x Male) (Wattys Winner 2021)",
    #     pov_info="Kane Emery"
    # ),
    # Story(
    #     name="Twenty Thousand Leagues Under The Sea",
    #     pov_info="Pierre Aronnax"
    # ),
    # Story(
    #     name="White Fang"
    # ),
]