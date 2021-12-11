from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from story_database import *
import os

WINDOW_SIZE = [ 800, 1200 ]

class FandomInfo:
    def __init__( self, name, db ):
        self.name = name
        self.db = db

class FandomInfoListItem( QListWidgetItem ):
    def __init__( self, fandomName ):
        super().__init__()
        self.name = fandomName
        self.setText( fandomName )
        #self.setFont( STENCIL_FONT )

class StoryDesc( QListWidgetItem ):
    def __init__( self, story ):
        super().__init__()
        self.story = story
        self.setText( story.__str__() )

class StoryListItem( QListWidgetItem ):
    def __init__( self, story ):
        super().__init__()
        self.story = story
        showString = story.title + " by " + story.author
        self.setText( showString )
        #self.setFont( STENCIL_FONT )

class MainWindow( QMainWindow ):
    def __init__( self ):
        super( MainWindow, self ).__init__()
        self.resize( WINDOW_SIZE[0], WINDOW_SIZE[1] )
        self.setStyleSheet( "background-color: lightGray;" )
        self._centralWidget = QWidget( self )
        self.setCentralWidget( self._centralWidget )
        self._verticalLayout = QVBoxLayout()
        self._centralWidget.setLayout( self._verticalLayout )
        self.fandoms = {}
        self.RefreshInfo()
        self.MainMenu()
        self.show()

    def RefreshInfo( self ):
        fandoms = {}
        dirs = [name for name in os.listdir( "fandoms/" ) if os.path.isdir( "fandoms/" + name )]
        for i in range( len( dirs ) ):
            fandom = dirs[i]
            fandomPath = "fandoms/" + fandom + "/"
            dbName = fandomPath + "databases/regular.bin"
            if os.path.exists( dbName ):
                storyDB = LoadStoryDB( dbName )
                fandoms[fandom] = FandomInfo( fandom, storyDB )

        self.fandoms = fandoms

    def _clearLayout( self, layout ):
        if layout is not None:
            for i in reversed( range( layout.count() ) ): 
                item = layout.itemAt( i )
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    self._clearLayout( item.layout() )

    #keyPressed = pyqtSignal(int)
    def keyPressEvent( self, event ):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            print( "Enter hit" )
        #elif event.key() == Qt.Key_Space:
        #    print( "space" )

    def OpenStoryUrl( self, storyListItem ):
        story = storyListItem.story
        QDesktopServices.openUrl( QUrl( story.GetUrl() ) )
    
    def FandomHome( self, s ):
        self._clearLayout( self._verticalLayout )
        fandomInfo = self.fandoms[s.text()]
        self.currentFandom = fandomInfo
        vlist = QListWidget( self )
        for story in fandomInfo.db.stories:
            vlist.addItem( StoryListItem( story ) )
        scrollBar = QScrollBar()
        vlist.setVerticalScrollBar( scrollBar )
        vlist.itemClicked.connect( self.OpenStoryUrl )
        #vlist.setCurrentRow( 5 )
        self._verticalLayout.addWidget( vlist )

    def MainMenu( self ):
        self.setWindowTitle( "Select Fandom" )
        self._clearLayout( self._verticalLayout )

        vlist = QListWidget( self )
        for fandomName in self.fandoms:
            vlist.addItem( QListWidgetItem( fandomName ) )
        scrollBar = QScrollBar()
        vlist.setVerticalScrollBar( scrollBar )
        vlist.itemClicked.connect( self.FandomHome )
        self._verticalLayout.addWidget( vlist )

if __name__ == "__main__":
    app = QApplication( [] )
    window = MainWindow()
    app.exec_()