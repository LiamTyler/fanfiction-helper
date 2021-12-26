from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
from story import EncodeNum, EncodeStr

PACKET_SIZE = 8192
WINDOW_SIZE = [ 800, 1200 ]

SERVER_CMD_REQUEST_FANDOMS = 2
SERVER_CMD_REQUEST_FANDOM_STORIES = 3

def SendDataToServer( data ):
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect( ('127.0.0.1', 27015) )
    s.sendall( data )
    return s

def ReceiveDataFromServer( s ):
    data = s.recv( PACKET_SIZE ).decode()
    p = data.find( '\0' )
    dataSize = int( data[:p] )
    receivedSize = len( data ) - p - 1
    while receivedSize != dataSize:
        newData = s.recv( PACKET_SIZE )
        if not newData:
            break
        receivedSize += len( newData )
        data += newData.decode()

    return data

class StoryListItem( QListWidgetItem ):
    def __init__( self, title, url ):
        super().__init__()
        self.title = title
        self.url = url
        showString = title
        self.setText( showString )

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
        self.MainMenu()
        self.show()

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
        url = storyListItem.url
        QDesktopServices.openUrl( QUrl( url ) )
    
    def FandomHome( self, fandom ):
        fandom = fandom.text()
        self._clearLayout( self._verticalLayout )
        self.setWindowTitle( "Fandom: " + fandom )

        s = SendDataToServer( EncodeNum( SERVER_CMD_REQUEST_FANDOM_STORIES ) + EncodeStr( fandom ) )
        data = ReceiveDataFromServer( s )

        split = data.split( '\0' )[1:-2]
        stories = split[::2]
        urls = split[1::2]
        numStories = len( split ) // 2
        vlist = QListWidget( self )
        for i in range(numStories):
            vlist.addItem( StoryListItem( stories[i], urls[i] ) )
        scrollBar = QScrollBar()
        vlist.setVerticalScrollBar( scrollBar )
        vlist.itemClicked.connect( self.OpenStoryUrl )
        self._verticalLayout.addWidget( vlist )

    def MainMenu( self ):
        self.setWindowTitle( "Select Fandom" )
        self._clearLayout( self._verticalLayout )

        s = SendDataToServer( EncodeNum( SERVER_CMD_REQUEST_FANDOMS ) )
        data = ReceiveDataFromServer( s )
        self.fandoms = data.split( '\0' )[1:-2]

        vlist = QListWidget( self )
        vlist.addItem( QListWidgetItem( "All" ) )
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
